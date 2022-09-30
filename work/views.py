import logging
from typing import Callable

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm
from django.shortcuts import render, redirect

from core.helper.view_utils import CommonInitFormViewTemplate
from work.forms import WorkForm

log = logging.getLogger(__name__)


# Create your views here.

class WorkInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'work/init_form.html', {'work_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('work:full_form', new_instance.iwork_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return WorkForm
