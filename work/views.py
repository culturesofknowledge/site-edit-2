import logging
import re
from collections.abc import Callable
from typing import Iterable, Any, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Model
from django.db.models.lookups import Exact, Lookup
from django.forms import BaseForm
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from core import constant
from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_WORK_IS_REPLY_TO, \
    REL_TYPE_WORK_MATCHES, REL_TYPE_COMMENT_DATE, REL_TYPE_WAS_SENT_FROM, REL_TYPE_COMMENT_ORIGIN, \
    REL_TYPE_COMMENT_DESTINATION, REL_TYPE_WAS_SENT_TO, REL_TYPE_COMMENT_ROUTE, REL_TYPE_FORMERLY_OWNED, \
    REL_TYPE_ENCLOSED_IN, REL_TYPE_COMMENT_RECEIPT_DATE, REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_STORED_IN, \
    REL_TYPE_COMMENT_PERSON_MENTIONED, REL_TYPE_MENTION, REL_TYPE_MENTION_PLACE, \
    REL_TYPE_MENTION_WORK, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_IS_RELATED_TO
from core.export_data import excel_maker, cell_values
from core.forms import WorkRecrefForm, PersonRecrefForm, ManifRecrefForm, CommentForm, LocRecrefForm
from core.helper import view_serv, lang_serv, model_serv, query_serv, renderer_serv, date_serv
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.form_serv import save_multi_rel_recref_formset
from core.helper.lang_serv import LangModelAdapter, NewLangForm
from core.helper.perm_serv import class_permission_required
from core.helper.query_serv import create_recref_lookup_fn
from core.helper.recref_handler import SingleRecrefHandler, RecrefFormsetHandler, SubjectHandler, ImageRecrefHandler, \
    TargetResourceFormsetHandler, MultiRecrefAdapterHandler
from core.helper.recref_serv import create_recref_if_field_exist
from core.helper.renderer_serv import RendererFactory
from core.helper.view_components import DownloadCsvHandler, HeaderValues
from core.helper.view_handler import FullFormHandler
from core.helper.view_serv import DefaultSearchView
from core.models import Recref, CofkLookupCatalogue
from institution import inst_serv
from location import location_serv
from location.models import CofkUnionLocation
from manifestation import manif_serv
from manifestation.manif_serv import create_manif_id
from manifestation.models import CofkUnionManifestation, CofkManifCommentMap, \
    CofkUnionLanguageOfManifestation, CofkManifImageMap
from person import person_serv
from person.models import CofkUnionPerson
from work import work_serv, subqueries
from work.forms import WorkAuthorRecrefForm, WorkAddresseeRecrefForm, \
    AuthorRelationChoices, AddresseeRelationChoices, PlacesForm, DatesForm, CorrForm, ManifForm, \
    ManifPersonRecrefAdapter, ScribeRelationChoices, \
    DetailsForm, WorkPersonRecrefAdapter, \
    CommonWorkForm, manif_type_choices, CompactSearchFieldset, ExpandedSearchFieldset, \
    ManifPersonMRRForm
from work.models import CofkWorkPersonMap, CofkUnionWork, CofkWorkCommentMap, CofkWorkResourceMap, \
    CofkUnionLanguageOfWork
from work.recref_adapter import WorkLocRecrefAdapter, ManifInstRecrefAdapter, WorkSubjectRecrefAdapter, \
    EarlierLetterRecrefAdapter, LaterLetterRecrefAdapter, EnclosureManifRecrefAdapter, EnclosedManifRecrefAdapter, \
    WorkCommentRecrefAdapter, ManifCommentRecrefAdapter, WorkResourceRecrefAdapter, ManifImageRecrefAdapter
from work.view_components import WorkFormDescriptor
from work.work_serv import DisplayableWork

log = logging.getLogger(__name__)


def create_search_fn_person_recref(rel_types: list) -> Callable:
    def _fn(f, v):
        return Q(**{
            'cofkworkpersonmap__person_id': v,
            'cofkworkpersonmap__relationship_type__in': rel_types,
        })

    return _fn


def create_lookup_fn_by_comment(rel_types: list) -> Callable:
    return create_recref_lookup_fn(rel_types, 'cofkworkcommentmap__comment',
                                   query_serv.comment_detail_fields)


def create_lookup_fn_by_resource(rel_types: list) -> Callable:
    return create_recref_lookup_fn(rel_types, 'cofkworkresourcemap__resource',
                                   query_serv.resource_detail_fields)


def lookup_fn_flags(lookup_fn, field_name, value):
    cond_map = [
        (r'Date\s+of\s+work\s+INFERRED', lambda: Q(date_of_work_inferred=1)),
        (r'Date\s+of\s+work\s+UNCERTAIN', lambda: Q(date_of_work_uncertain=1)),
        (r'Date\s+of\s+work\s+APPROXIMATE', lambda: Q(date_of_work_approx=1)),
        (r'Author\s*/\s*sender\s+INFERRED', lambda: Q(authors_inferred=1)),
        (r'Author\s*/\s*sender\s+UNCERTAIN', lambda: Q(authors_uncertain=1)),
        (r'Addressee\s+INFERRED', lambda: Q(addressees_inferred=1)),
        (r'Addressee\s+UNCERTAIN', lambda: Q(addressees_uncertain=1)),
        (r'Origin\s+INFERRED', lambda: Q(origin_inferred=1)),
        (r'Origin\s+UNCERTAIN', lambda: Q(origin_uncertain=1)),
        (r'Destination\s+INFERRED', lambda: Q(destination_inferred=1)),
        (r'Destination\s+UNCERTAIN', lambda: Q(destination_uncertain=1)),
    ]

    query = Q()
    for pattern, q in cond_map:
        if re.search(pattern, value, re.IGNORECASE):
            query |= q()
    return query


def create_search_fn_location_recref(rel_types: list) -> Callable:
    def _fn(f, v):
        return Q(**{
            'cofkworklocationmap__location_id': v,
            'cofkworklocationmap__relationship_type__in': rel_types,
        })

    return _fn


class BasicWorkFFH(FullFormHandler):
    def __init__(self, pk, template_name, request_data=None, request=None, *args, **kwargs):
        self.request_iwork_id = None
        super().__init__(pk, *args,
                         request_data=request_data or None,
                         request=request, **kwargs)
        self.template_name = template_name

        # this variable will be assigned after **valid POST request** saved work
        self.saved_work = None

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.request_iwork_id = pk
        if self.request_iwork_id:
            self.work = get_object_or_404(CofkUnionWork, iwork_id=self.request_iwork_id)
        else:
            self.work = None

        self.safe_work = self.work or CofkUnionWork()

        self.common_work_form = CommonWorkForm(request_data, initial={
            'catalogue': self.safe_work.original_catalogue_id,
            'work_to_be_deleted': self.safe_work.work_to_be_deleted,
        })
        catalogue_list = [('', None)] + [(c.catalogue_name, c.catalogue_code) for c in
                                         CofkLookupCatalogue.objects.all().order_by('catalogue_name')]
        self.common_work_form.fields['catalogue_list'].widget.choices = catalogue_list
        self.common_work_form.fields['catalogue'].widget.choices = [(i[1], i[0]) for i in catalogue_list]

    def create_context(self, is_save_success=False):
        context = super().create_context()
        context.update({
                           'iwork_id': self.request_iwork_id
                       } | WorkFormDescriptor(self.work).create_context()
                       | view_serv.create_is_save_success_context(is_save_success)
                       )
        return context

    def render_form(self, request, is_save_success=False):
        return render(request, self.template_name, self.create_context(is_save_success))

    def save_work(self, request, work: CofkUnionWork):
        # ----- save work
        if not work.work_id:
            work.work_id = work_serv.create_work_id(work.iwork_id)

        # handle catalogue
        self.common_work_form.is_valid()
        cat_code = self.common_work_form.cleaned_data.get('catalogue')
        if cat_code and work.original_catalogue_id != cat_code:
            log.info('change original_catalogue_id from [{}] to [{}]'.format(
                work.original_catalogue_id, cat_code))
            work.original_catalogue_id = cat_code

        # handle work_to_be_deleted
        work.work_to_be_deleted = self.common_work_form.cleaned_data.get('work_to_be_deleted', 0)

        if work.description != (cur_desc := work_serv.get_recref_display_name(work)):
            work.description = cur_desc

        work.update_current_user_timestamp(request.user.username)
        work.save()
        log.info(f'save work {work}')
        self.saved_work = work

        return work


class PlacesFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/places_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        self.origin_loc_handler = SingleRecrefHandler(
            form_field_name='selected_origin_location_id',
            rel_type=REL_TYPE_WAS_SENT_FROM,
            create_recref_adapter_fn=WorkLocRecrefAdapter,
        )
        self.destination_loc_handler = SingleRecrefHandler(
            form_field_name='selected_destination_location_id',
            rel_type=REL_TYPE_WAS_SENT_TO,
            create_recref_adapter_fn=WorkLocRecrefAdapter,
        )

        dates_form_initial = (
                {}
                | self.origin_loc_handler.create_init_dict(self.work)
                | self.destination_loc_handler.create_init_dict(self.work)
        )
        self.places_form = PlacesForm(request_data, instance=self.work, initial=dates_form_initial)

        # comments
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='origin_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_ORIGIN,
            parent=self.safe_work,
        ))
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='destination_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_DESTINATION,
            parent=self.safe_work,
        ))
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='route_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_ROUTE,
            parent=self.safe_work,
        ))

    def save(self, request):
        if not self.is_any_changed():
            log.debug('skip save places when no changed')
            return

        work = self.save_work(request, self.places_form.instance)
        self.save_all_recref_formset(work, request)

        self.origin_loc_handler.upsert_recref_if_field_exist(
            self.places_form, work, request.user.username
        )
        self.destination_loc_handler.upsert_recref_if_field_exist(
            self.places_form, work, request.user.username
        )


class DatesFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/dates_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        self.dates_form = DatesForm(request_data, instance=self.work)

        # comments
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='date_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_DATE,
            parent=self.safe_work,
        ))

    def save(self, request):
        if not self.is_any_changed():
            log.debug('skip save dates when no changed')
            return

        work = self.save_work(request, self.dates_form.instance)
        self.save_all_recref_formset(work, request)


class CorrFFH(BasicWorkFFH):

    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/corr_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        self.corr_form = CorrForm(request_data, instance=self.work)

        # recref
        self.author_formset = WorkAuthorRecrefForm.create_formset_by_records(
            request_data,
            self.work.cofkworkpersonmap_set.iterator() if self.work else [],
            prefix='work_author'
        )

        self.addressee_formset = WorkAddresseeRecrefForm.create_formset_by_records(
            request_data,
            self.work.cofkworkpersonmap_set.iterator() if self.work else [],
            prefix='work_addressee'
        )

        # comment
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='author_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_AUTHOR,
            parent=self.safe_work,
        ))
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='addressee_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_ADDRESSEE,
            parent=self.safe_work,
        ))

        # letters
        self.earlier_letter_handler = MultiRecrefAdapterHandler(
            request_data, name='earlier_letter',
            recref_adapter=EarlierLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_IS_REPLY_TO,
        )
        self.later_letter_handler = MultiRecrefAdapterHandler(
            request_data, name='later_letter',
            recref_adapter=LaterLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_IS_REPLY_TO,
        )
        self.matching_letter_handler = MultiRecrefAdapterHandler(
            request_data, name='matching_letter',
            recref_adapter=EarlierLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_MATCHES,
        )

    def save(self, request):
        if not self.is_any_changed():
            log.debug('skip save corr when no changed')
            return

        work = self.save_work(request, self.corr_form.instance)

        # save selected recref
        create_work_person_map_if_field_exist(
            self.corr_form, work, request.user.username,
            selected_id_field_name='selected_author_id',
            rel_type=AuthorRelationChoices.CREATED,
        )
        create_work_person_map_if_field_exist(
            self.corr_form, work, request.user.username,
            selected_id_field_name='selected_addressee_id',
            rel_type=AddresseeRelationChoices.ADDRESSED_TO,
        )

        # handle author_formset
        save_multi_rel_recref_formset(self.author_formset, work, request)
        save_multi_rel_recref_formset(self.addressee_formset, work, request)

        # handle all comments
        self.save_all_recref_formset(work, request)

        # handle recref_handler
        self.maintain_all_recref_records(request, work)


class ManifFFH(BasicWorkFFH):
    def __init__(self, iwork_id, template_name, manif_id=None,
                 request_data=None, request=None, *args, **kwargs):
        super().__init__(iwork_id, template_name, *args,
                         manif_id=manif_id, request_data=request_data, request=request, **kwargs)

    def load_data(self, iwork_id, *args,
                  manif_id=None, request_data=None, request=None, **kwargs):
        super().load_data(iwork_id, request_data=request_data, request=request)

        if manif_id:
            self.manif = get_object_or_404(CofkUnionManifestation, manifestation_id=manif_id)
        else:
            self.manif = None

        self.inst_handler = SingleRecrefHandler(
            form_field_name='selected_inst_id',
            rel_type=REL_TYPE_STORED_IN,
            create_recref_adapter_fn=ManifInstRecrefAdapter,
        )

        self.safe_manif = self.manif or CofkUnionManifestation()

        manif_form_initial = {}
        if self.manif is not None:
            manif_form_initial.update(
                self.inst_handler.create_init_dict(self.manif)
            )
        self.manif_form = ManifForm(request_data or None,
                                    instance=self.manif, initial=manif_form_initial)
        self.new_lang_form = NewLangForm.create_new_lang_form(self.safe_manif.language_set.iterator())

        self.former_recref_handler = MultiRecrefAdapterHandler(
            request_data, name='former',
            recref_adapter=ManifPersonRecrefAdapter(self.safe_manif),
            recref_form_class=PersonRecrefForm,
            rel_type=REL_TYPE_FORMERLY_OWNED,
        )
        self.scribe_recref_formset = ManifPersonMRRForm.create_formset_by_records(
            request_data,
            self.safe_manif.cofkmanifpersonmap_set.iterator(),
            prefix='scribe'
        )

        self.edit_lang_formset = lang_serv.create_lang_formset(
            self.safe_manif.language_set.iterator(),
            lang_rec_id_name='lang_manif_id',
            request_data=request_data,
            prefix='edit_lang')

        # comments
        self.add_recref_formset_handler(ManifCommentFormsetHandler(
            prefix='date_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_DATE,
            parent=self.safe_manif,
        ))
        self.add_recref_formset_handler(ManifCommentFormsetHandler(
            prefix='receipt_date_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_RECEIPT_DATE,
            parent=self.safe_manif,
        ))
        self.add_recref_formset_handler(ManifCommentFormsetHandler(
            prefix='manif_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_REFERS_TO,
            parent=self.safe_manif,
        ))

        # enclosures
        self.enclosure_manif_handler = MultiRecrefAdapterHandler(
            request_data, name='enclosure_manif',
            recref_adapter=EnclosureManifRecrefAdapter(self.safe_manif),
            recref_form_class=ManifRecrefForm,
            rel_type=REL_TYPE_ENCLOSED_IN,
        )
        self.enclosed_manif_handler = MultiRecrefAdapterHandler(
            request_data, name='enclosed_manif',
            recref_adapter=EnclosedManifRecrefAdapter(self.safe_manif),
            recref_form_class=ManifRecrefForm,
            rel_type=REL_TYPE_ENCLOSED_IN,
        )

        self.img_recref_handler = ManifImageRecrefHandler(request_data, request and request.FILES,
                                                          parent=self.safe_manif)

    def create_context(self, is_save_success=False):
        context = super().create_context(is_save_success=is_save_success)
        if self.manif:
            context['manif_id'] = self.manif.manifestation_id

        if work := model_serv.get_safe(CofkUnionWork, iwork_id=self.request_iwork_id):
            manif_set = []
            for _manif in work.manif_set.iterator():
                _manif: CofkUnionManifestation
                inst = _manif.find_selected_inst()
                inst = inst and inst.inst
                _manif.inst_display_name = inst_serv.get_recref_display_name(inst)
                _manif.lang_list_str = ', '.join(
                    (l.language_code.language_name for l in _manif.language_set.iterator())
                )
                manif_set.append(_manif)

            context['manif_set'] = manif_set

        return context

    def save(self, request):

        # handle remove manif list
        del_manif_id_list = request.POST.getlist('del_manif_id_list')
        for _manif_id in del_manif_id_list:
            log.info(f'del manif -- [{_manif_id}]')
            get_object_or_404(CofkUnionManifestation, pk=_manif_id).delete()

        # handle common_work_form
        if self.common_work_form.has_changed():
            self.save_work(request, self.work)

        # handle save
        manif: CofkUnionManifestation = self.manif_form.instance
        if manif.manifestation_id in del_manif_id_list:
            log.debug(f'current manif[{manif.manifestation_id}] removed[{del_manif_id_list}] no need to save')
            return

        log.debug(f'changed_data : {self.manif_form.changed_data}')
        manif.work = get_object_or_404(CofkUnionWork, iwork_id=self.request_iwork_id)
        if not manif.manifestation_id:
            manif.manifestation_id = create_manif_id(self.request_iwork_id)

        manif.save()
        log.info(f'save manif {manif}')

        # comments
        self.save_all_recref_formset(manif, request)
        self.maintain_all_recref_records(request, manif)

        # language
        lang_serv.maintain_lang_records(self.edit_lang_formset,
                                        lambda pk: CofkUnionLanguageOfManifestation.objects.get(pk=pk))

        lang_serv.add_new_lang_record(request.POST.getlist('lang_note'),
                                      request.POST.getlist('lang_name'),
                                      manif.manifestation_id,
                                      ManifLangModelAdapter(), )

        create_recref_if_field_exist(self.manif_form, manif, request.user.username,
                                     selected_id_field_name='selected_scribe_id',
                                     rel_type=ScribeRelationChoices.HANDWROTE,
                                     recref_adapter=ManifPersonMRRForm.create_recref_adapter())
        save_multi_rel_recref_formset(self.scribe_recref_formset, manif, request)
        self.img_recref_handler.save(manif, request)

        self.inst_handler.upsert_recref_if_field_exist(
            self.manif_form, manif, request.user.username)


class ResourcesFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/resources_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)
        self.add_recref_formset_handler(WorkResourceFormsetHandler(
            request_data=request_data,
            parent=self.work,
        ))

    def save(self, request):
        if not self.is_any_changed():
            log.debug('skip save resources when no changed')
            return

        self.save_work(request, self.work)
        self.save_all_recref_formset(self.work, request)


class DetailsFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/details_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        self.details_form = DetailsForm(request_data, instance=self.work)

        # comment
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='people_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_PERSON_MENTIONED,
            parent=self.safe_work,
        ))
        self.add_recref_formset_handler(WorkCommentFormsetHandler(
            prefix='general_comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_REFERS_TO,
            parent=self.safe_work,
        ))

        # related recref
        self.people_recref_handler = MultiRecrefAdapterHandler(
            request_data, name='people',
            recref_adapter=WorkPersonRecrefAdapter(self.safe_work),
            recref_form_class=PersonRecrefForm,
            rel_type=REL_TYPE_MENTION,
        )
        self.place_recref_handler = MultiRecrefAdapterHandler(
            request_data, name='place',
            recref_adapter=WorkLocRecrefAdapter(self.safe_work),
            recref_form_class=LocRecrefForm,
            rel_type=REL_TYPE_MENTION_PLACE,
        )
        self.work_recref_handler = MultiRecrefAdapterHandler(
            request_data, name='work',
            recref_adapter=EarlierLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_MENTION_WORK,
        )

        # language
        self.lang_formset = lang_serv.create_lang_formset(
            self.safe_work.language_set.iterator(),
            lang_rec_id_name='lang_work_id',
            request_data=request_data,
            prefix='lang')
        self.new_lang_form = NewLangForm.create_new_lang_form(self.safe_work.language_set.iterator())

        self.subject_handler = SubjectHandler(WorkSubjectRecrefAdapter(self.safe_work))

    def create_context(self, is_save_success=False):
        context: dict = super().create_context(is_save_success=is_save_success)
        context.update(self.subject_handler.create_context())
        return context

    def has_changed(self, request):
        return (super(DetailsFFH, self).is_any_changed()
                or self.subject_handler.has_changed(request)
                or request.POST.getlist('lang_name'))

    def save(self, request):
        if not self.has_changed(request):
            log.debug('skip save details when no changed')
            return
        work = self.save_work(request, self.details_form.instance)

        # language
        lang_serv.maintain_lang_records(self.lang_formset,
                                        lambda pk: CofkUnionLanguageOfWork.objects.get(pk=pk))

        lang_serv.add_new_lang_record(request.POST.getlist('lang_note'),
                                      request.POST.getlist('lang_name'),
                                      work.work_id,
                                      WorkLangModelAdapter(), )

        self.save_all_recref_formset(work, request)
        self.maintain_all_recref_records(request, work)
        self.subject_handler.save(request, work)


class ManifLangModelAdapter(LangModelAdapter):
    def create_instance_by_owner_id(self, owner_id):
        m = CofkUnionLanguageOfManifestation()
        m.manifestation_id = owner_id
        return m


class WorkLangModelAdapter(LangModelAdapter):

    def create_instance_by_owner_id(self, owner_id):
        m = CofkUnionLanguageOfWork()
        m.work_id = owner_id
        return m


def create_work_person_map_if_field_exist(form: BaseForm, work, username,
                                          selected_id_field_name,
                                          rel_type, ):
    if not (_id := form.cleaned_data.get(selected_id_field_name)):
        return

    work_person_map = CofkWorkPersonMap()
    work_person_map.person = get_object_or_404(CofkUnionPerson, pk=_id)
    work_person_map.work = work
    work_person_map.relationship_type = rel_type
    work_person_map.update_current_user_timestamp(username)
    work_person_map.save()

    return work_person_map


class BasicWorkFormView(LoginRequiredMixin, View):

    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        raise NotImplementedError()

    @property
    def cur_vname(self):
        raise NotImplementedError()

    @staticmethod
    def get_form_work_instance(fhandler: BasicWorkFFH) -> CofkUnionWork | None:
        forms = fhandler.every_form_formset
        works = (getattr(f, 'instance', None) for f in forms)
        works = (i for i in works if isinstance(i, CofkUnionWork))
        return next(works, fhandler.work)

    def resp_after_saved(self, request, fhandler):

        iwork_id = fhandler.request_iwork_id
        if fhandler.saved_work:
            iwork_id = fhandler.saved_work.iwork_id

        url = reverse(self.cur_vname, args=[iwork_id])
        url = view_serv.append_callback_save_success_parameter(request, url)
        return redirect(url)

    @class_permission_required(constant.PM_CHANGE_WORK)
    def post(self, request, iwork_id=None, *args, **kwargs):
        fhandler = self.create_fhandler(request, iwork_id=iwork_id, *args, **kwargs)
        if fhandler.is_invalid():
            return fhandler.render_form(request)
        fhandler.prepare_cleaned_data()
        fhandler.save(request)
        return self.resp_after_saved(request, fhandler)

    def get(self, request, iwork_id=None, *args, **kwargs):
        return self.create_fhandler(request, iwork_id, *args, **kwargs).render_form(
            request, is_save_success=view_serv.mark_callback_save_success(request))


class ManifView(BasicWorkFormView):
    @property
    def cur_vname(self):
        return 'work:manif_init'

    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return ManifFFH(iwork_id, template_name='work/manif_base.html',
                        request_data=request.POST or None,
                        request=request, *args, **kwargs)

    def resp_after_saved(self, request, fhandler):
        manif_id = fhandler.manif_form.instance.manifestation_id
        if not manif_id or not model_serv.is_exist(CofkUnionManifestation, {'manifestation_id': manif_id}):
            return redirect('work:manif_init', fhandler.request_iwork_id)

        url = reverse('work:manif_update',
                      args=[fhandler.request_iwork_id, manif_id])
        url = view_serv.append_callback_save_success_parameter(request, url)
        return redirect(url)


class CorrView(BasicWorkFormView):

    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return CorrFFH(iwork_id, request_data=request.POST, request=request)

    @property
    def cur_vname(self):
        return 'work:corr_form'


class DatesView(BasicWorkFormView):
    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return DatesFFH(iwork_id, request_data=request.POST, request=request)

    @property
    def cur_vname(self):
        return 'work:dates_form'


class PlacesView(BasicWorkFormView):
    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return PlacesFFH(iwork_id, request_data=request.POST, request=request)

    @property
    def cur_vname(self):
        return 'work:places_form'


class ResourcesView(BasicWorkFormView):
    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return ResourcesFFH(iwork_id, request_data=request.POST, request=request)

    @property
    def cur_vname(self):
        return 'work:resources_form'


class DetailsView(BasicWorkFormView):

    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return DetailsFFH(iwork_id, request_data=request.POST, request=request)

    @property
    def cur_vname(self):
        return 'work:details_form'


def get_overview_persons_names_by_rel_type(work: CofkUnionWork, rel_type):
    return (person_serv.get_recref_display_name(p) for p in
            work.cofkworkpersonmap_set.filter(relationship_type=rel_type))


class LinkData:
    @property
    def name(self):
        raise NotImplementedError()

    @property
    def link(self):
        raise NotImplementedError()


class PersonLinkData(LinkData):
    def __init__(self, model):
        self.model: CofkUnionPerson = model

    @property
    def name(self):
        return person_serv.get_recref_display_name(self.model)

    @property
    def link(self):
        return person_serv.get_form_url(self.model.iperson_id)


class WorkLinkData(LinkData):
    def __init__(self, model):
        self.model: CofkUnionWork = model

    @property
    def name(self):
        return work_serv.get_recref_display_name(self.model)

    @property
    def link(self):
        return work_serv.get_form_url(self.model.iwork_id)


class LocationLinkData(LinkData):
    def __init__(self, model):
        self.model: CofkUnionLocation = model

    @property
    def name(self):
        return location_serv.get_recref_display_name(self.model)

    @property
    def link(self):
        return location_serv.get_form_url(self.model.location_id)


def to_link_data_list(link_data_factory, related_manager, rel_type):
    return (link_data_factory(m) for m in related_manager.filter(relationship_type=rel_type))


def _to_lang_str(lang: CofkUnionLanguageOfWork):
    lang_str = lang.language_code.language_name
    if lang.notes:
        lang_str = lang_str + f' ({lang.notes})'
    return lang_str


def to_person_link_list(work, rel_type):
    return (PersonLinkData(r.person) for r in
            work.cofkworkpersonmap_set.filter(relationship_type=rel_type))


def to_location_link_list(work, rel_type):
    return (LocationLinkData(r.location) for r in
            work.cofkworklocationmap_set.filter(relationship_type=rel_type))


def to_overview_manif(manif: CofkUnionManifestation):
    if repo := manif.cofkmanifinstmap_set.first():
        manif.repo_name = repo.inst.institution_name

    manif.type_display_name = dict(manif_type_choices).get(manif.manifestation_type, '')
    manif.manifestation_receipt_calendar_display = date_serv.decode_calendar(manif.manifestation_receipt_calendar)

    return manif


@login_required()
def overview_view(request, iwork_id):
    if request.POST:
        return redirect('work:overview_form', iwork_id=iwork_id)

    work = get_object_or_404(CofkUnionWork, iwork_id=iwork_id)

    context = dict(
        iwork_id=work.iwork_id,
        work=work,
        work_display_name=work_serv.get_recref_display_name(work),

        notes_work=work_serv.find_related_comment_names(work, REL_TYPE_COMMENT_DATE),
        notes_author=work_serv.find_related_comment_names(work, REL_TYPE_COMMENT_AUTHOR),
        notes_addressee=work_serv.find_related_comment_names(work, REL_TYPE_COMMENT_ADDRESSEE),
        notes_people=work_serv.find_related_comment_names(work, REL_TYPE_COMMENT_PERSON_MENTIONED),
        notes_general=work_serv.find_related_comment_names(work, REL_TYPE_COMMENT_REFERS_TO),

        author_link_list=to_person_link_list(work, constant.REL_TYPE_CREATED),
        sender_link_list=to_person_link_list(work, constant.REL_TYPE_SENT),
        signed_link_list=to_person_link_list(work, constant.REL_TYPE_SIGNED),

        recipient_link_list=to_person_link_list(work, constant.REL_TYPE_WAS_ADDRESSED_TO),
        intended_link_list=to_person_link_list(work, constant.REL_TYPE_INTENDED_FOR),

        reply_to_link_list=[WorkLinkData(r.work_to) for r in
                            work.work_from_set.filter(relationship_type=constant.REL_TYPE_WORK_IS_REPLY_TO)],
        answered_link_list=[WorkLinkData(r.work_from) for r in
                            work.work_to_set.filter(relationship_type=constant.REL_TYPE_WORK_IS_REPLY_TO)],
        matches_link_list=[WorkLinkData(r.work_to) for r in
                           work.work_from_set.filter(relationship_type=constant.REL_TYPE_WORK_MATCHES)],

        origin_link_list=to_location_link_list(work, constant.REL_TYPE_WAS_SENT_FROM),
        destination_link_list=to_location_link_list(work, constant.REL_TYPE_WAS_SENT_TO),

        language=', '.join(map(_to_lang_str, work.language_set.iterator())),
        subjects=', '.join(w.subject.subject_desc for w in work.cofkworksubjectmap_set.iterator()),

        people_link_list=to_person_link_list(work, constant.REL_TYPE_MENTION),
        places_link_list=to_location_link_list(work, constant.REL_TYPE_MENTION_PLACE),
        work_mention_link_list=(WorkLinkData(r.work_to) for r in
                                work.work_from_set.filter(relationship_type=constant.REL_TYPE_MENTION_WORK)),
        work_be_mention_link_list=(WorkLinkData(r.work_from) for r in
                                   work.work_to_set.filter(relationship_type=constant.REL_TYPE_MENTION_WORK)),
        manif_set=list(map(to_overview_manif, work.manif_set.iterator())),
        original_calendar_display=date_serv.decode_calendar(work.original_calendar),
    )

    context.update(WorkFormDescriptor(work).create_context())

    return render(request, 'work/overview_form.html', context)


class WorkQuickInitView(CorrView):
    def resp_after_saved(self, request, fhandler):
        return redirect('work:return_quick_init', self.get_form_work_instance(fhandler).iwork_id)


@login_required
def return_quick_init(request, pk):
    work = CofkUnionWork.objects.get(iwork_id=pk)
    return view_serv.render_return_quick_init(
        request, 'Work',
        work_serv.get_recref_display_name(work),
        work_serv.get_recref_target_id(work),
    )


class WorkSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def entity(self) -> str:
        return 'work,works'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('addressees_searchable', 'Addressee',),
            ('creators_searchable', 'Author/sender',),
            ('date_of_work_std', 'Date for ordering (in original calendar)',),
            ('date_of_work_as_marked', 'Date of work as marked',),
            ('date_of_work_std_day', 'Day',),
            ('description', 'Description',),
            ('places_to_searchable', 'Destination (standardised)',),
            ('editors_notes', 'Editors\' notes',),
            # ('flags', 'Flags',),
            ('language_of_work', 'Language of work',),
            ('change_user', 'Last changed by',),
            ('change_timestamp', 'Last edit',),
            ('manifestations_searchable', 'Manifestations',),
            ('date_of_work_std_month', 'Month',),
            ('places_from_searchable', 'Origin (standardised)',),
            ('origin_as_marked', 'Origin as marked',),
            ('original_catalogue', 'Original catalogue',),
            ('work_to_be_deleted', 'Record to be deleted',),
            # ('related_resources', 'Related resources',),
            ('accession_code', 'Source of record',),
            ('iwork_id', 'Work ID',),
            ('date_of_work_std_year', 'Year',),
        ]

    @property
    def default_sort_by_choice(self) -> int:
        return 2

    @property
    def default_order(self):
        return 'asc'

    @property
    def search_field_fn_maps(self) -> dict[str, Lookup]:
        return {
            'work_to_be_deleted': lambda f, v: Exact(F(f), '0' if v == 'On' else '1'),
            'person_sent_pk': create_search_fn_person_recref(AuthorRelationChoices.values),
            'person_rec_pk': create_search_fn_person_recref(AddresseeRelationChoices.values),
            'person_sent_rec_pk': create_search_fn_person_recref(AuthorRelationChoices.values
                                                                 + AddresseeRelationChoices.values),
            'person_mention_pk': create_search_fn_person_recref([REL_TYPE_MENTION]),
            'location_sent_pk': create_search_fn_location_recref([REL_TYPE_WAS_SENT_FROM]),
            'location_rec_pk': create_search_fn_location_recref([REL_TYPE_WAS_SENT_TO]),
            'location_sent_rec_pk': create_search_fn_location_recref(
                [REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO]),
        } | query_serv.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                               'change_timestamp') \
            | query_serv.create_from_to_datetime('date_of_work_std_from', 'date_of_work_std_to',
                                                 'date_of_work_std',
                                                 convert_fn=date_serv.search_datestr_to_db_datestr, )

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionWork.objects.none()

        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        queries = query_serv.create_queries_by_field_fn_maps(request_data, self.search_field_fn_maps)

        search_fields_maps = {
            'language_of_work': [
                'language_set__language_code__language_name',
                'language_set__language_code__code_639_3',
                'language_set__language_code__code_639_1',
            ],
            'original_catalogue': [
                'original_catalogue__catalogue_code',
                'original_catalogue__catalogue_name',
            ],
            'images': [
                'manif_set__images__image_filename',
            ],
        }

        queries.extend(
            query_serv.create_queries_by_lookup_field(
                request_data, self.search_fields,
                search_fields_maps=search_fields_maps,
                search_fields_fn_maps={
                    'notes_on_authors': create_lookup_fn_by_comment([REL_TYPE_COMMENT_AUTHOR]),
                    'related_resources': create_lookup_fn_by_resource([REL_TYPE_IS_RELATED_TO]),
                    'general_notes': create_lookup_fn_by_comment([REL_TYPE_COMMENT_REFERS_TO]),
                    'flags': lookup_fn_flags,
                })
        )
        return create_queryset_by_queries(DisplayableWork, queries, sort_by=sort_by)

    @property
    def simplified_query(self) -> list[str]:
        simplified_query = super().simplified_query

        if self.search_field_fn_maps:
            work_to_be_deleted = (self.request_data['work_to_be_deleted']
                                  if 'work_to_be_deleted' in self.request_data else None)

            if work_to_be_deleted:
                if work_to_be_deleted == 'on':
                    simplified_query.append(f'Is to be deleted.')

            _from = self.request_data['date_of_work_std_from'] if 'date_of_work_std_from' in self.request_data else None
            _to = self.request_data['date_of_work_std_to'] if 'date_of_work_std_to' in self.request_data else None

            if _to and _from:
                simplified_query.append(f'Date for ordering (in original calendar) between {_from} and {_to}.')
            elif _to:
                simplified_query.append(f'Date for ordering (in original calendar) before {_to}.')
            elif _from:
                simplified_query.append(f'Date for ordering (in original calendar) after {_from}.')

        return simplified_query

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer('work/expanded_search_table_layout.html')

    @property
    def compact_search_results_renderer_factory(self) -> RendererFactory:
        # Compact search results for works are also table formatted
        return renderer_serv.create_table_search_results_renderer('work/compact_search_table_layout.html')

    @property
    def return_quick_init_vname(self) -> str:
        return 'work:return_quick_init'

    @property
    def query_fieldset_list(self) -> Iterable:
        return [CompactSearchFieldset(self.request_data.dict())]

    @property
    def expanded_query_fieldset_list(self) -> Iterable:
        return [ExpandedSearchFieldset(self.request_data.dict())]

    @property
    def csv_export_setting(self):
        if not self.has_perms(constant.PM_EXPORT_FILE_WORK):
            return None

        return (lambda: view_serv.create_export_file_name('work', 'csv'),
                lambda: DownloadCsvHandler(WorkCsvHeaderValues()).create_csv_file,
                constant.PM_EXPORT_FILE_WORK,
                )

    @property
    def excel_export_setting(self) -> tuple[Callable[[], str], Callable[[Iterable, str], Any], str] | None:
        """ overrider this to enable download csv """

        if not self.has_perms(constant.PM_EXPORT_FILE_WORK):
            return None

        return (lambda: view_serv.create_export_file_name('work', 'xlsx'),
                lambda: excel_maker.create_work_excel,
                constant.PM_EXPORT_FILE_WORK,
                )

    @property
    def app_name(self) -> str:
        return 'work'


class WorkCommentFormsetHandler(RecrefFormsetHandler):

    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return WorkCommentRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkWorkCommentMap.objects.filter(work=parent, comment=target).first()


class ManifCommentFormsetHandler(RecrefFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return ManifCommentRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkManifCommentMap.objects.filter(manifestation=parent, comment=target).first()


class WorkResourceFormsetHandler(TargetResourceFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return WorkResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkWorkResourceMap.objects.filter(work=parent, resource=target).first()


class ManifImageRecrefHandler(ImageRecrefHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return ManifImageRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkManifImageMap.objects.filter(manif=parent, image=target).first()


class WorkCsvHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "Description",
            "Editor's notes",
            "Date of work as marked",
            "Year",
            "Month",
            "Day",
            "Date in original calendar",
            "Creators",
            "Notes on authors/senders",
            "Places from",
            "Origin as marked",
            "Addressees",
            "Places to",
            "Destination as marked",
            "Flags",
            "Images",
            "Manifestations",
            "Related resources",
            "Language of work",
            "Subjects",
            "Abstract",
            "People mentioned",
            "Keywords",
            "General notes",
            "Original catalogue",
            "Source of record",
            "Record to be deleted",
            "Work ID",
            "Date/time of last change",
            "Changed by user",
        ]

    def obj_to_values(self, obj) -> Iterable[str]:
        obj: DisplayableWork
        values = (
            obj.description,
            obj.editors_notes,
            obj.date_of_work_as_marked,
            obj.date_of_work_std_year,
            obj.date_of_work_std_month,
            obj.date_of_work_std_day,
            obj.date_of_work_std_gregorian,
            obj.queryable_people(REL_TYPE_CREATED, is_details=True),
            cell_values.notes(obj.author_comments),
            obj.places_from_for_display,
            obj.origin_as_marked,
            obj.queryable_people(REL_TYPE_WAS_ADDRESSED_TO, is_details=True),
            obj.places_to_for_display,
            obj.destination_as_marked,
            work_serv.flags(obj),
            obj.images,
            ' -- '.join(' '.join(manif_serv.get_manif_details(m))
                        for m in obj.manif_set.all()),
            cell_values.resource_str_by_list(wrm.resource for wrm in obj.cofkworkresourcemap_set.all()),
            obj.language_of_work,
            obj.subjects_for_display,
            obj.abstract,
            obj.people_mentioned,
            obj.keywords,
            obj.general_notes,
            obj.original_catalogue and obj.original_catalogue.catalogue_name,
            obj.accession_code,
            obj.work_to_be_deleted,
            obj.iwork_id,
            cell_values.simple_datetime(obj.change_timestamp),
            obj.change_user,
        )
        return values


def create_queryset_by_queries(model_class: Type[Model], queries: Iterable[Q] = None,
                               sort_by=None):
    # some fields in annotate for sorting and filtering, it could be different with frontend display
    annotate = {
        'addressees_searchable': subqueries.create_joined_person_ann_field([REL_TYPE_WAS_ADDRESSED_TO]),
        'creators_searchable': subqueries.create_joined_person_ann_field([REL_TYPE_CREATED]),
        'mentioned_searchable': subqueries.create_joined_person_ann_field([REL_TYPE_MENTION]),
        'sender_or_recipient': subqueries.create_joined_person_ann_field([REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO]),
        'places_from_searchable': subqueries.create_joined_location_ann_field(
            [REL_TYPE_WAS_SENT_FROM],
            [
                'cofkworklocationmap__location__location_name',
                'origin_as_marked',
            ]
        ),
        'places_to_searchable': subqueries.create_joined_location_ann_field(
            [REL_TYPE_WAS_SENT_TO],
            [
                'cofkworklocationmap__location__location_name',
                'destination_as_marked',
            ]
        ),
        'origin_or_destination': subqueries.create_joined_location_ann_field(
            [REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM],
            [
                'cofkworklocationmap__location__location_name',
                'origin_as_marked',
                'destination_as_marked',
            ]
        ),
        'manifestations_searchable': subqueries.create_joined_manif_ann_field(),
    }

    queryset = model_class.objects.filter()
    queryset = query_serv.update_queryset(queryset, model_class, queries=queries,
                                          sort_by=sort_by,
                                          annotate=annotate
                                          )
    queryset = queryset.prefetch_related('cofkworkpersonmap_set__person',
                                         'cofkworklocationmap_set__location',
                                         'cofkworkresourcemap_set__resource',
                                         'cofkworkcommentmap_set__comment',
                                         'work_to_set__work_from',
                                         'work_from_set__work_to',
                                         'language_set__language_code',
                                         'subjects',
                                         'manif_set',
                                         'manif_set__images',
                                         'manif_set__cofkmanifinstmap_set__inst',
                                         'manif_set__manif_from_set__manif_to',
                                         'manif_set__manif_to_set__manif_from',
                                         ).select_related('original_catalogue')

    return queryset
