import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect

from core.constant import REL_TYPE_COMMENT_AUTHOR
from core.forms import CommentForm
from core.helper import view_utils, model_utils
from core.helper.view_utils import DefaultSearchView, FullFormHandler
from person.models import CofkUnionPerson
from work.forms import WorkForm, WorkPersonMapForm
from work.models import CofkWorkPersonMap, CofkUnionWork, create_work_id, CofkWorkComment

log = logging.getLogger(__name__)


class WorkFullFormHandler(FullFormHandler):

    def __init__(self, pk, template_name, request_data=None, request=None, *args, **kwargs):
        super().__init__(pk, *args, request_data=request_data, request=request, **kwargs)
        self.template_name = template_name

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        if pk:
            self.work = get_object_or_404(CofkUnionWork, iwork_id=pk)
        else:
            self.work = None

        self.work_form = WorkForm(request_data or None, instance=self.work)
        if self.work is None:
            return

        self.work_person_formset = WorkPersonMapForm.create_formset_by_records(
            request_data,
            self.work.cofkworkpersonmap_set.iterator()
        )

        self.author_comment_formset = view_utils.create_formset(
            CommentForm, post_data=request_data,
            prefix='author_comment',
            initial_list=model_utils.models_to_dict_list(self.work.author_comments),
        )

        # self.loc_handler = LocRecrefHandler(
        #     request_data, model_list=self.person.cofkpersonlocationmap_set.iterator(), )
        #
        # self.org_handler = PersonRecrefHandler(request_data, person_type='organisation',
        #                                        person=self.person)
        # self.parent_handler = PersonRecrefHandler(request_data, person_type='parent',
        #                                           person=self.person)
        # self.children_handler = PersonRecrefHandler(request_data, person_type='children',
        #                                             person=self.person)
        #
        # self.employer_handler = PersonRecrefHandler(request_data, person_type='employer',
        #                                             person=self.person)
        # self.employee_handler = PersonRecrefHandler(request_data, person_type='employee',
        #                                             person=self.person)
        # self.teacher_handler = PersonRecrefHandler(request_data, person_type='teacher',
        #                                            person=self.person)
        # self.student_handler = PersonRecrefHandler(request_data, person_type='student',
        #                                            person=self.person)
        # self.patron_handler = PersonRecrefHandler(request_data, person_type='patron',
        #                                           person=self.person)
        # self.protege_handler = PersonRecrefHandler(request_data, person_type='protege',
        #                                            person=self.person)
        # self.other_handler = PersonRecrefHandler(request_data, person_type='other',
        #                                          name='person_other',
        #                                          person=self.person)
        #
        # self.comment_formset = view_utils.create_formset(CommentForm, post_data=request_data,
        #                                                  prefix='comment',
        #                                                  initial_list=model_utils.related_manager_to_dict_list(
        #                                                      self.person.comments), )
        # self.res_formset = view_utils.create_formset(ResourceForm, post_data=request_data,
        #                                              prefix='res',
        #                                              initial_list=model_utils.related_manager_to_dict_list(
        #                                                  self.person.resources), )
        # self.img_handler = ImageHandler(request_data, request and request.FILES, self.person.images)

    def render_form(self, request):

        context = (
                dict(self.all_named_form_formset())
                | self.create_all_recref_context()
        )
        return render(request, self.template_name, context)


def create_relation_if_sender_person_id_exist(work_form: WorkForm, work, username):
    sender_person_id = work_form.cleaned_data.get('sender_person_id')
    if not sender_person_id:
        return

    work_person_map = CofkWorkPersonMap()
    work_person_map.person = get_object_or_404(CofkUnionPerson, pk=sender_person_id)
    work_person_map.work = work
    work_person_map.relationship_type = 'created'
    work_person_map.update_current_user_timestamp(username)
    work_person_map.save()


@login_required
def init_form(request):
    fhandler = WorkFullFormHandler(None, 'work/init_form.html',
                                   request_data=request.POST, request=request)
    # work_form = WorkForm(request.POST or None)
    if request.method == 'POST':
        work_form = fhandler.work_form
        if work_form.is_valid():
            work: CofkUnionWork = work_form.instance
            work.work_id = create_work_id(work.iwork_id)
            work.save()

            create_relation_if_sender_person_id_exist(work_form, work, request.user.username)

            return redirect('work:full_form', work.iwork_id)

    return fhandler.render_form(request)


@login_required
def full_form(request, iwork_id):
    fhandler = WorkFullFormHandler(iwork_id, 'work/init_form.html',
                                   request_data=request.POST, request=request)

    if request.method == 'POST':

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

        fhandler.work_form.save()

        create_relation_if_sender_person_id_exist(
            fhandler.work_form, fhandler.work, request.user.username
        )

        # handle work_person_formset
        _forms = (f for f in fhandler.work_person_formset if f.has_changed())
        for form in _forms:
            form: WorkPersonMapForm
            form.create_or_delete(fhandler.work, request.user.username)

        # KTODO work.save
        fhandler.work.refresh_from_db()

        view_utils.save_m2m_relation_records(
            fhandler.author_comment_formset,
            lambda c: model_utils.get_or_create(
                CofkWorkComment,
                **dict(work_id=fhandler.work.work_id,
                       comment_id=c.comment_id,
                       relationship_type=REL_TYPE_COMMENT_AUTHOR)
            ),
            request.user.username,
            model_id_name='comment_id',
        )

        # reload data
        fhandler.load_data(iwork_id, request_data=None, request=request)

    # KTODO
    return fhandler.render_form(request)


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
