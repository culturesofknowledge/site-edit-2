import logging
from typing import Optional, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_WORK_IS_REPLY_TO, \
    REL_TYPE_WORK_MATCHES, REL_TYPE_COMMENT_DATE, REL_TYPE_WAS_SENT_FROM, REL_TYPE_COMMENT_ORIGIN, \
    REL_TYPE_COMMENT_DESTINATION, REL_TYPE_WAS_SENT_TO, REL_TYPE_COMMENT_ROUTE
from core.forms import WorkRecrefForm
from core.helper import view_utils, recref_utils
from core.helper.view_utils import DefaultSearchView, FullFormHandler, CommentFormsetHandler
from person.models import CofkUnionPerson
from work import work_utils
from work.forms import WorkForm, WorkPersonRecrefForm, WorkAuthorRecrefForm, WorkAddresseeRecrefForm, \
    AuthorRelationChoices, AddresseeRelationChoices
from work.models import CofkWorkPersonMap, CofkUnionWork, create_work_id, CofkWorkComment, CofkWorkWorkMap, \
    CofkWorkLocationMap

log = logging.getLogger(__name__)


class WorkCommentFormsetHandler(CommentFormsetHandler):
    def __init__(self, prefix, request_data, rel_type, comments_query_fn, context_name=None):
        super().__init__(prefix, request_data, rel_type, comments_query_fn,
                         comment_class=CofkWorkComment, owner_id_name='work_id',
                         context_name=context_name, )


def get_location_id(model: models.Model):
    return model and model.location_id


class WorkFullFormHandler(FullFormHandler):

    def __init__(self, pk, template_name, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, *args, request_data=request_data, request=request, **kwargs)
        self.template_name = template_name

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        if pk:
            self.work = get_object_or_404(CofkUnionWork, iwork_id=pk)
        else:
            self.work = None

        work_form_initial = {}
        if self.work is not None:
            work_form_initial.update({
                'selected_origin_location_id': get_location_id(self.work.origin_location),
                'selected_destination_location_id': get_location_id(self.work.destination_location),
            })

        self.work_form = WorkForm(request_data or None, instance=self.work, initial=work_form_initial)

        tmp_work = self.work or CofkUnionWork()

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

        # comments
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='author_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_AUTHOR,
            comments_query_fn=tmp_work.find_comments_by_rel_type,
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='addressee_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ADDRESSEE,
            comments_query_fn=tmp_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='date_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_DATE,
            comments_query_fn=tmp_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='origin_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ORIGIN,
            comments_query_fn=tmp_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='destination_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_DESTINATION,
            comments_query_fn=tmp_work.find_comments_by_rel_type
        ))
        self.add_comment_handler(WorkCommentFormsetHandler(
            prefix='route_comment',
            request_data=request_data,
            rel_type=REL_TYPE_COMMENT_ROUTE,
            comments_query_fn=tmp_work.find_comments_by_rel_type
        ))

        # letters
        self.earlier_letter_handler = EarlierLetterRecrefHandler(
            request_data,
            tmp_work.work_from_set.filter(relationship_type=REL_TYPE_WORK_IS_REPLY_TO).iterator())
        self.later_letter_handler = LaterLetterRecrefHandler(
            request_data,
            tmp_work.work_to_set.filter(relationship_type=REL_TYPE_WORK_IS_REPLY_TO).iterator())
        self.matching_letter_handler = EarlierLetterRecrefHandler(
            request_data,
            tmp_work.work_from_set.filter(relationship_type=REL_TYPE_WORK_MATCHES).iterator(),
            name='matching_letter',
            rel_type=REL_TYPE_WORK_MATCHES,
        )

    def render_form(self, request):

        context = (
                dict(self.all_named_form_formset())
                | self.create_all_recref_context()
        )
        return render(request, self.template_name, context)


def create_work_person_map_if_field_exist(work_form: WorkForm, work, username,
                                          selected_id_field_name,
                                          rel_type, ):
    if not (_id := work_form.cleaned_data.get(selected_id_field_name)):
        return

    work_person_map = CofkWorkPersonMap()
    work_person_map.person = get_object_or_404(CofkUnionPerson, pk=_id)  # KTODO change to .person_id = ??
    work_person_map.work = work
    work_person_map.relationship_type = rel_type
    work_person_map.update_current_user_timestamp(username)
    work_person_map.save()

    return work_person_map


def upsert_work_location_map_if_field_exist(work_form: WorkForm, work, username,
                                            selected_id_field_name,
                                            rel_type,
                                            org_map=None):
    if not (_id := work_form.cleaned_data.get(selected_id_field_name)):
        return

    work_location_map = org_map or CofkWorkLocationMap()
    work_location_map.location_id = _id
    work_location_map.work = work
    work_location_map.relationship_type = rel_type
    work_location_map.update_current_user_timestamp(username)
    work_location_map.save()

    return work_location_map


class WorkInitView(LoginRequiredMixin, View):

    @staticmethod
    def create_fhandler(request):
        return WorkFullFormHandler(None, 'work/init_form.html',
                                   request_data=request.POST, request=request)

    def resp_after_saved(self, request, fhandler):
        return redirect('work:full_form', fhandler.work_form.instance.iwork_id)

    def post(self, request, *args, **kwargs):
        fhandler = self.create_fhandler(request)
        if is_invalid(fhandler):
            return fhandler.render_form(request)
        save_full_form_handler(fhandler, request)
        return self.resp_after_saved(request, fhandler)

    def get(self, request, *args, **kwargs):
        return self.create_fhandler(request).render_form(request)


class WorkQuickInitView(WorkInitView):
    def resp_after_saved(self, request, fhandler):
        return redirect('work:return_quick_init', fhandler.work_form.instance.iwork_id)


@login_required
def return_quick_init(request, pk):
    work = CofkUnionWork.objects.get(iwork_id=pk)
    return view_utils.render_return_quick_init(
        request, 'Work',
        work_utils.get_recref_display_name(work),
        work_utils.get_recref_target_id(work),
    )


@login_required
def full_form(request, iwork_id):
    fhandler = WorkFullFormHandler(iwork_id, 'work/init_form.html',
                                   request_data=request.POST, request=request)

    if request.method == 'POST':
        if is_invalid(fhandler):
            return fhandler.render_form(request)
        save_full_form_handler(fhandler, request)

        # reload data
        fhandler.load_data(iwork_id, request_data=None, request=request)

    # KTODO
    return fhandler.render_form(request)


def is_invalid(fhandler: WorkFullFormHandler, ):
    # KTODO make this list generic
    form_formsets = [*fhandler.all_form_formset,
                     # fhandler.img_handler.img_form,
                     # fhandler.img_handler.image_formset,
                     ]
    for h in fhandler.all_recref_handlers:
        form_formsets.extend([h.new_form, h.update_formset, ])

    return view_utils.any_invalid_with_log(form_formsets)


def save_multi_rel_recref_formset(multi_rel_recref_formset, work, request):
    _forms = (f for f in multi_rel_recref_formset if f.has_changed())
    for form in _forms:
        form: WorkPersonRecrefForm
        form.create_or_delete(work, request.user.username)


def save_full_form_handler(fhandler: WorkFullFormHandler, request):
    # define form_formsets
    # KTODO make this list generic
    form_formsets = [*fhandler.all_form_formset,
                     # fhandler.img_handler.img_form,
                     # fhandler.img_handler.image_formset,
                     ]
    for h in fhandler.all_recref_handlers:
        form_formsets.extend([h.new_form, h.update_formset, ])

    # ----- validate
    if view_utils.any_invalid_with_log(form_formsets):
        return fhandler.render_form(request)

    # ----- save
    work: CofkUnionWork = fhandler.work_form.instance
    if not work.work_id:
        work.work_id = create_work_id(work.iwork_id)
    work.save()
    log.info(f'save work {work}')  # KTODO fix iwork_id plus more than 1

    # handle selected_person_id
    create_work_person_map_if_field_exist(
        fhandler.work_form, work, request.user.username,
        selected_id_field_name='selected_author_id',
        rel_type=AuthorRelationChoices.CREATED,
    )
    create_work_person_map_if_field_exist(
        fhandler.work_form, work, request.user.username,
        selected_id_field_name='selected_addressee_id',
        rel_type=AddresseeRelationChoices.ADDRESSED_TO,
    )
    upsert_work_location_map_if_field_exist(
        fhandler.work_form, work, request.user.username,
        selected_id_field_name='selected_origin_location_id',
        rel_type=REL_TYPE_WAS_SENT_FROM,
        org_map=work.origin_location,
    )
    upsert_work_location_map_if_field_exist(
        fhandler.work_form, work, request.user.username,
        selected_id_field_name='selected_destination_location_id',
        rel_type=REL_TYPE_WAS_SENT_TO,
        org_map=work.destination_location,
    )

    # handle author_formset
    save_multi_rel_recref_formset(fhandler.author_formset, work, request)
    save_multi_rel_recref_formset(fhandler.addressee_formset, work, request)

    # handle all comments
    fhandler.save_all_comment_formset(work.work_id, request)

    # handle recref_handler
    for r in fhandler.all_recref_handlers:
        r.maintain_record(request, work)


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
    # KTODO tobe define
    work = CofkUnionWork.objects.get(work_id=work_id)
    return work and work.work_id


class LetterRecrefHandler(view_utils.MultiRecrefHandler):
    def __init__(self, request_data, model_list, name, target_id_name,
                 rel_type='is_reply_to'):
        initial_list = (m.__dict__ for m in model_list)
        initial_list = (recref_utils.convert_to_recref_form_dict(r, target_id_name, find_work_rec_name)
                        for r in initial_list)
        self.rel_type = rel_type
        super().__init__(request_data, name=name, initial_list=initial_list,
                         recref_form_class=WorkRecrefForm)

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkWorkWorkMap

    def define_work_from_to(self, parent_instance, target_instance):
        """ define which one is work_from, work_to
        :return : work_from, work_to
        """
        raise NotImplementedError()

    def create_recref_by_new_form(self, target_id, parent_instance) -> Optional[models.Model]:
        if not (target_instance := CofkUnionWork.objects.get(work_id=target_id)):
            log.warning(f"create recref fail, work not found -- {target_id} ")
            return None

        work_work: CofkWorkWorkMap = CofkWorkWorkMap()
        work_work.work_from, work_work.work_to = self.define_work_from_to(
            parent_instance, target_instance)
        work_work.relationship_type = self.rel_type
        return work_work


class EarlierLetterRecrefHandler(LetterRecrefHandler):
    def __init__(self, request_data, model_list, name='earlier_letter',
                 rel_type=REL_TYPE_WORK_IS_REPLY_TO):
        super().__init__(request_data, model_list, name=name,
                         target_id_name='work_to_id',
                         rel_type=rel_type, )

    def define_work_from_to(self, parent_instance, target_instance):
        return parent_instance, target_instance


class LaterLetterRecrefHandler(LetterRecrefHandler):

    def __init__(self, request_data, model_list, name='later_letter',
                 rel_type=REL_TYPE_WORK_IS_REPLY_TO):
        super().__init__(request_data, model_list, name=name,
                         target_id_name='work_from_id',
                         rel_type=rel_type)

    def define_work_from_to(self, parent_instance, target_instance):
        return target_instance, parent_instance
