from typing import Callable, Iterable

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from core.helper import renderer_utils
from core.helper.view_utils import DefaultSearchView
from core.models import Iso639LanguageCode


class LanguageSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def entity(self) -> str:
        return 'Languages,Language'

    def get_queryset(self):
        return Iso639LanguageCode.objects.all()

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer(
            'core/language_expanded_search_table_layout.html'
        )


def fav_remove(request):
    data = request.POST

    return JsonResponse({})


def fav_add(request):
    data = request.POST

    return JsonResponse({})
