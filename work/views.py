import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from core.helper.view_utils import DefaultSearchView
from person.models import CofkUnionPerson
from work.forms import WorkForm

log = logging.getLogger(__name__)


@login_required
def init_form(request):
    work_form = WorkForm(request.POST or None)
    if request.method == 'POST':
        if work_form.is_valid():
            pass

        pass

    return render(request, 'work/init_form.html', {'work_form': work_form})


@login_required
def full_form(request, iwork_id):
    # KTODO
    work_form = WorkForm()
    return render(request, 'work/init_form.html', {'work_form': work_form})


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
