import logging
from abc import ABC
from typing import Optional, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.forms import Form, ModelForm, BaseForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_WORK_IS_REPLY_TO, \
    REL_TYPE_WORK_MATCHES, REL_TYPE_COMMENT_DATE, REL_TYPE_WAS_SENT_FROM, REL_TYPE_COMMENT_ORIGIN, \
    REL_TYPE_COMMENT_DESTINATION, REL_TYPE_WAS_SENT_TO, REL_TYPE_COMMENT_ROUTE, REL_TYPE_FORMERLY_OWNED, \
    REL_TYPE_ENCLOSED_IN, REL_TYPE_COMMENT_RECEIPT_DATE, REL_TYPE_COMMENT_REFERS_TO
from core.forms import WorkRecrefForm, PersonRecrefForm, ManifRecrefForm
from core.helper import view_utils, lang_utils
from core.helper.lang_utils import LangModelAdapter
from core.helper.view_utils import DefaultSearchView, FullFormHandler, CommentFormsetHandler, RecrefFormAdapter
from core.models import Recref
from manifestation import manif_utils
from manifestation.models import CofkUnionManifestation, CofkManifCommentMap, create_manif_id, CofkManifManifMap, \
    CofkUnionLanguageOfManifestation
from person.models import CofkUnionPerson
from work import work_utils
from work.forms import WorkPersonRecrefForm, WorkAuthorRecrefForm, WorkAddresseeRecrefForm, \
    AuthorRelationChoices, AddresseeRelationChoices, PlacesForm, DatesForm, CorrForm, ManifForm, \
    ManifPersonRecrefAdapter, ManifPersonRecrefForm, ScribeRelationChoices
from work.models import CofkWorkPersonMap, CofkUnionWork, create_work_id, CofkWorkComment, CofkWorkWorkMap, \
    CofkWorkLocationMap

log = logging.getLogger(__name__)


class WorkCommentFormsetHandler(CommentFormsetHandler):
    def __init__(self, prefix, request_data, rel_type, comments_query_fn, context_name=None):
        super().__init__(prefix, request_data, rel_type, comments_query_fn,
                         comment_class=CofkWorkComment, owner_id_name='work_id',
                         context_name=context_name, )


class ManifCommentFormsetHandler(CommentFormsetHandler):
    def __init__(self, prefix, request_data, rel_type, comments_query_fn, context_name=None):
        super().__init__(prefix, request_data, rel_type, comments_query_fn,
                         comment_class=CofkManifCommentMap, owner_id_name='manifestation_id',
                         context_name=context_name, )


def get_location_id(model: models.Model):
    return model and model.location_id


# class DatesFFH(BasicWorkFFH):
#     pass


class BasicWorkFFH(FullFormHandler):
    def __init__(self, pk, template_name, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, *args,
                         request_data=request_data or None,
                         request=request, **kwargs)
        self.template_name = template_name

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        if pk:
            self.work = get_object_or_404(CofkUnionWork, iwork_id=pk)
        else:
            self.work = None

        self.safe_work = self.work or CofkUnionWork()  # KTODO iwork_id sequence number +1 by this ??

    def render_form(self, request):

        context = (
                dict(self.all_named_form_formset())
                | self.create_all_recref_context()
        )
        return render(request, self.template_name, context)

    def is_invalid(self):
        form_formsets = (f for f in self.every_form_formset if f.has_changed())
        return view_utils.any_invalid_with_log(form_formsets)

    def prepare_cleaned_data(self):
        for f in self.every_form_formset:
            f.is_valid()

    def save_work(self, request, work_form: ModelForm):
        # ----- save work
        work: CofkUnionWork = work_form.instance
        log.debug(f'changed_data : {work_form.changed_data}')
        if not work.work_id:
            work.work_id = create_work_id(work.iwork_id)  # KTODO fix
        work.save()
        log.info(f'save work {work}')  # KTODO fix iwork_id plus more than 1
        return work


class PlacesFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/places_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        dates_form_initial = {}
        if self.work is not None:
            dates_form_initial.update({
                'selected_origin_location_id': get_location_id(self.work.origin_location),
                'selected_destination_location_id': get_location_id(self.work.destination_location),
            })
        self.places_form = PlacesForm(request_data, instance=self.work, initial=dates_form_initial)

        # comments
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='origin_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ORIGIN,
            comments_query_fn=self.safe_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='destination_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_DESTINATION,
            comments_query_fn=self.safe_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='route_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ROUTE,
            comments_query_fn=self.safe_work.find_comments_by_rel_type
        ))

    def save(self, request):
        work = self.save_work(request, self.places_form)
        self.save_all_comment_formset(work.work_id, request)

        upsert_work_location_map_if_field_exist(
            self.places_form, work, request.user.username,
            selected_id_field_name='selected_origin_location_id',
            rel_type=REL_TYPE_WAS_SENT_FROM,
            org_map=work.origin_location,
        )
        upsert_work_location_map_if_field_exist(
            self.places_form, work, request.user.username,
            selected_id_field_name='selected_destination_location_id',
            rel_type=REL_TYPE_WAS_SENT_TO,
            org_map=work.destination_location,
        )


class DatesFFH(BasicWorkFFH):
    def __init__(self, pk, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, 'work/dates_form.html', *args, request_data=request_data, request=request, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        super().load_data(pk, request_data=request_data, request=request)

        self.dates_form = DatesForm(request_data, instance=self.work)

        # comments
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='date_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_DATE,
            comments_query_fn=self.safe_work.find_comments_by_rel_type
        ))

    def save(self, request):
        work = self.save_work(request, self.dates_form)
        self.save_all_comment_formset(work.work_id, request)


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
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='author_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_AUTHOR,
            comments_query_fn=self.safe_work.find_comments_by_rel_type,
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='addressee_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ADDRESSEE,
            comments_query_fn=self.safe_work.find_comments_by_rel_type
        ))

        # letters
        self.earlier_letter_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='earlier_letter',
            recref_adapter=EarlierLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_IS_REPLY_TO,
        )
        self.later_letter_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='later_letter',
            recref_adapter=LaterLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_IS_REPLY_TO,
        )
        self.matching_letter_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='matching_letter',
            recref_adapter=EarlierLetterRecrefAdapter(self.safe_work),
            recref_form_class=WorkRecrefForm,
            rel_type=REL_TYPE_WORK_MATCHES,
        )

    def save(self, request):
        work = self.save_work(request, self.corr_form)

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
        self.save_all_comment_formset(work.work_id, request)

        # handle recref_handler
        self.maintain_all_recref_records(request, work)


class ManifFFH(BasicWorkFFH):
    def __init__(self, iwork_id, template_name, manif_id=None,
                 request_data=None, request=None, *args, **kwargs):
        super().__init__(iwork_id, template_name, *args,
                         manif_id=manif_id, request_data=request_data, request=request, **kwargs)

    def load_data(self, iwork_id, *args,
                  manif_id=None, request_data=None, request=None, **kwargs):
        # super().load_data(iwork_id, request_data=request_data, request=request)

        self.iwork_id = iwork_id

        if manif_id:
            self.manif = get_object_or_404(CofkUnionManifestation, manifestation_id=manif_id)
        else:
            self.manif = None
        self.safe_manif = self.manif or CofkUnionManifestation()

        self.manif_form = ManifForm(request_data or None,
                                    instance=self.manif)

        self.former_recref_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='former',
            recref_adapter=ManifPersonRecrefAdapter(self.safe_manif),
            recref_form_class=PersonRecrefForm,
            rel_type=REL_TYPE_FORMERLY_OWNED,
        )
        self.scribe_recref_formset = ManifPersonRecrefForm.create_formset_by_records(
            request_data,
            self.safe_manif.cofkmanifpersonmap_set.iterator(),
            prefix='scribe'
        )

        self.edit_lang_formset = lang_utils.create_lang_formset(
            self.safe_manif.language_set.iterator(),
            lang_rec_id_name='lang_manif_id',
            request_data=request_data,
            prefix='edit_lang')

        # comments
        self.add_comment_handler(ManifCommentFormsetHandler(
            prefix='date_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_DATE,
            comments_query_fn=self.safe_manif.find_comments_by_rel_type
        ))
        self.add_comment_handler(ManifCommentFormsetHandler(
            prefix='receipt_date_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_RECEIPT_DATE,
            comments_query_fn=self.safe_manif.find_comments_by_rel_type
        ))
        self.add_comment_handler(ManifCommentFormsetHandler(
            prefix='manif_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_REFERS_TO,
            comments_query_fn=self.safe_manif.find_comments_by_rel_type
        ))

        # enclosures
        self.enclosure_manif_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='enclosure_manif',
            recref_adapter=EnclosureManifRecrefAdapter(self.safe_manif),
            recref_form_class=ManifRecrefForm,
            rel_type=REL_TYPE_ENCLOSED_IN,
        )
        self.enclosed_manif_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='enclosed_manif',
            recref_adapter=EnclosedManifRecrefAdapter(self.safe_manif),
            recref_form_class=ManifRecrefForm,
            rel_type=REL_TYPE_ENCLOSED_IN,
        )

    def save(self, request):

        manif: CofkUnionManifestation = self.manif_form.instance
        log.debug(f'changed_data : {self.manif_form.changed_data}')
        manif.work = get_object_or_404(CofkUnionWork, iwork_id=self.iwork_id)
        if not manif.manifestation_id:
            manif.manifestation_id = create_manif_id(self.iwork_id)
        manif.save()
        log.info(f'save manif {manif}')  # KTODO fix iwork_id plus more than 1

        # comments
        self.save_all_comment_formset(manif.manifestation_id, request)
        self.maintain_all_recref_records(request, manif)

        lang_utils.maintain_lang_records(self.edit_lang_formset,
                                         lambda pk: CofkUnionLanguageOfManifestation.objects.get(pk=pk))

        lang_utils.add_new_lang_record(request.POST.getlist('lang_note'),
                                       request.POST.getlist('lang_name'),
                                       manif.manifestation_id,
                                       ManifLangModelAdapter(), )

        create_recref_if_field_exist(self.manif_form, manif, request.user.username,
                                     selected_id_field_name='selected_scribe_id',
                                     rel_type=ScribeRelationChoices.HANDWROTE,
                                     recref_adapter=ManifPersonRecrefForm.create_recref_adapter())
        save_multi_rel_recref_formset(self.scribe_recref_formset, manif, request)


class ManifLangModelAdapter(LangModelAdapter):
    def create_instance_by_owner_id(self, owner_id):
        m = CofkUnionLanguageOfManifestation()
        m.manifestation_id = owner_id
        return m


def create_recref_if_field_exist(form: BaseForm, work, username,
                                 selected_id_field_name,
                                 rel_type,
                                 recref_adapter: RecrefFormAdapter,
                                 ):
    if not (_id := form.cleaned_data.get(selected_id_field_name)):
        return

    recref = recref_adapter.create_recref(rel_type,
                                          parent_instance=work,
                                          target_instance=recref_adapter.find_target_instance(_id),
                                          username=username)
    recref.save()
    return recref


def create_work_person_map_if_field_exist(form: BaseForm, work, username,
                                          selected_id_field_name,
                                          rel_type, ):
    if not (_id := form.cleaned_data.get(selected_id_field_name)):
        return

    work_person_map = CofkWorkPersonMap()
    work_person_map.person = get_object_or_404(CofkUnionPerson, pk=_id)  # KTODO change to .person_id = ??
    work_person_map.work = work
    work_person_map.relationship_type = rel_type
    work_person_map.update_current_user_timestamp(username)
    work_person_map.save()

    return work_person_map


def upsert_work_location_map_if_field_exist(form: Form, work, username,
                                            selected_id_field_name,
                                            rel_type,
                                            org_map=None):
    if not (_id := form.cleaned_data.get(selected_id_field_name)):
        return

    work_location_map = org_map or CofkWorkLocationMap()
    work_location_map.location_id = _id
    work_location_map.work = work
    work_location_map.relationship_type = rel_type
    work_location_map.update_current_user_timestamp(username)
    work_location_map.save()

    return work_location_map


class BasicWorkFormView(LoginRequiredMixin, View):
    goto_vname_map = {
        'corr': 'work:corr_form',
        'dates': 'work:dates_form',
        'places': 'work:places_form',
        'manif': 'work:manif_init',
    }

    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        raise NotImplementedError()

    @property
    def cur_vname(self):
        raise NotImplementedError()

    @staticmethod
    def get_form_work_instance(fhandler: FullFormHandler) -> CofkUnionWork | None:
        forms = fhandler.all_form_formset
        works = (getattr(f, 'instance', None) for f in forms)
        works = (i for i in works if isinstance(i, CofkUnionWork))
        return next(works, None)

    def resp_after_saved(self, request, fhandler):
        goto = request.POST.get('__goto')
        vname = self.goto_vname_map.get(goto, self.cur_vname)
        return redirect(vname, self.get_form_work_instance(fhandler).iwork_id)

    def post(self, request, iwork_id=None, *args, **kwargs):
        fhandler = self.create_fhandler(request, iwork_id=iwork_id, *args, **kwargs)
        if fhandler.is_invalid():
            return fhandler.render_form(request)
        fhandler.prepare_cleaned_data()
        fhandler.save(request)
        return self.resp_after_saved(request, fhandler)

    def get(self, request, iwork_id=None, *args, **kwargs):
        return self.create_fhandler(request, iwork_id, *args, **kwargs).render_form(request)


class BasicManifView(BasicWorkFormView, ABC):

    def resp_after_saved(self, request, fhandler):
        if goto := request.POST.get('__goto'):
            vname = self.goto_vname_map.get(goto, self.cur_vname)
            return redirect(vname, fhandler.iwork_id)

        return redirect('work:manif_update',
                        fhandler.manif_form.instance.work.iwork_id,
                        fhandler.manif_form.instance.manifestation_id)


class ManifInitView(BasicManifView):
    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return ManifFFH(iwork_id, template_name='work/manif_init.html',
                        request_data=request.POST or None,
                        request=request)

    @property
    def cur_vname(self):
        return 'work:manif_init'


class ManifUpdateView(BasicManifView):
    @staticmethod
    def create_fhandler(request, iwork_id=None, *args, **kwargs):
        return ManifFFH(iwork_id, template_name='work/manif_update.html',
                        request_data=request.POST or None,
                        request=request, *args, **kwargs)

    @property
    def cur_vname(self):
        return 'work:manif_update'


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


class WorkQuickInitView(CorrView):
    def resp_after_saved(self, request, fhandler):
        return redirect('work:return_quick_init', self.get_form_work_instance(fhandler).iwork_id)


@login_required
def return_quick_init(request, pk):
    work = CofkUnionWork.objects.get(iwork_id=pk)
    return view_utils.render_return_quick_init(
        request, 'Work',
        work_utils.get_recref_display_name(work),
        work_utils.get_recref_target_id(work),
    )


def save_multi_rel_recref_formset(multi_rel_recref_formset, work, request):
    _forms = (f for f in multi_rel_recref_formset if f.has_changed())
    for form in _forms:
        form: WorkPersonRecrefForm
        form.create_or_delete(work, request.user.username)


class WorkSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def title(self) -> str:
        return 'Work'

    def get_queryset(self):
        queryset = CofkUnionPerson.objects.all()
        return queryset

    @property
    def return_quick_init_vname(self) -> str:
        return 'work:return_quick_init'


def find_work_rec_name(work_id) -> Optional[str]:
    return work_utils.get_recref_display_name(CofkUnionWork.objects.get(work_id=work_id))


class WorkWorkRecrefAdapter(view_utils.RecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return find_work_rec_name(target_id)

    def recref_class(self) -> Type[Recref]:
        return CofkWorkWorkMap

    def find_target_instance(self, target_id):
        return CofkUnionWork.objects.get(work_id=target_id)


class EarlierLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def set_parent_target_instance(self, recref, parent, target):
        recref.work_from = parent
        recref.work_to = target

    def find_recref_records(self, rel_type):
        return self.work.work_from_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'work_to_id'


class LaterLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def set_parent_target_instance(self, recref, parent, target):
        recref.work_from = parent
        recref.work_to = target

    def find_recref_records(self, rel_type):
        return self.work.work_to_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'work_from_id'


class ManifManifRecrefAdapter(view_utils.RecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return manif_utils.get_recref_display_name(self.find_target_instance(target_id))

    def recref_class(self) -> Type[Recref]:
        return CofkManifManifMap

    def find_target_instance(self, target_id):
        return CofkUnionManifestation.objects.get(pk=target_id)


class EnclosureManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def set_parent_target_instance(self, recref, parent, target):
        recref.manif_from = parent
        recref.manif_to = target

    def find_recref_records(self, rel_type):
        return self.manif.manif_from_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'manif_to_id'


class EnclosedManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def set_parent_target_instance(self, recref, parent, target):
        recref.manif_from = target
        recref.manif_to = parent

    def find_recref_records(self, rel_type):
        return self.manif.manif_to_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'manif_from_id'
