import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect

from core.helper.view_utils import DefaultSearchView
from person.models import CofkUnionPerson
from work.forms import WorkForm, WorkPersonMapForm
from work.models import CofkWorkPersonMap, CofkUnionWork, create_work_id

log = logging.getLogger(__name__)


@login_required
def init_form(request):
    work_form = WorkForm(request.POST or None)
    if request.method == 'POST':
        if work_form.is_valid():
            work: CofkUnionWork = work_form.instance
            work.work_id = create_work_id(work.iwork_id)
            work.save()

            work_person_map = CofkWorkPersonMap()
            work_person_map.person = get_object_or_404(CofkUnionPerson,
                                                       pk=work_form.cleaned_data.get('sender_person_id'))
            work_person_map.work = work
            work_person_map.relationship_type = 'created'
            work_person_map.update_current_user_timestamp(request.user.username)
            work_person_map.save()

            return redirect('work:full_form', work.iwork_id)

    return render(request, 'work/init_form.html', {'work_form': work_form})


@login_required
def full_form(request, iwork_id):
    work = get_object_or_404(CofkUnionWork, iwork_id=iwork_id)

    work_person_formset = WorkPersonMapForm.create_formset_by_records(
        request.POST,
        work.cofkworkpersonmap_set.iterator()
    )

    if request.method == 'POST':
        _forms = (f for f in work_person_formset if f.has_changed())
        for form in _forms:
            form: WorkPersonMapForm
            form.create_or_delete(work, request.user.username)

        # KTODO work.save
        work.save()
        work.refresh_from_db()

        # reload data
        work_person_formset = WorkPersonMapForm.create_formset_by_records(
            None, work.cofkworkpersonmap_set.iterator()
        )

    # KTODO
    work_form = WorkForm()
    return render(request, 'work/init_form.html', {
        'work_form': work_form,
        'work_person_formset': work_person_formset,
    })


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
