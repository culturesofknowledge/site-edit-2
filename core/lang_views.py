from typing import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core import constant
from core.helper import renderer_serv, query_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView
from core.lang_forms import LangSearchFieldset
from core.models import Iso639LanguageCode, CofkUnionFavouriteLanguage


def lookup_fn_is_favorite(lookup, field, value):
    if value is None:
        return Q()
    else:
        return Q(cofkunionfavouritelanguage__isnull=(value != '1'))


class LanguageSearchView(PermissionRequiredMixin, LoginRequiredMixin, DefaultSearchView):
    permission_required = constant.PM_CHANGE_LANGUAGE

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('language_name', 'Language name',),
        ]

    @property
    def entity(self) -> str:
        return 'Language,Languages'

    @property
    def default_order(self) -> str:
        return 'asc'

    def get_queryset(self):
        model_class = Iso639LanguageCode
        if not self.request_data:
            return model_class.objects.none()

        queries = []
        queries.extend(
            query_serv.create_queries_by_lookup_field(self.request_data, self.search_fields,
                                                         search_fields_fn_maps={
                                                              'is_favorite': lookup_fn_is_favorite,
                                                         }
                                                      )
        )
        queryset = model_class.objects.filter()
        queryset = query_serv.update_queryset(queryset, model_class, queries=queries,
                                               sort_by=self.get_sort_by())

        return queryset

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer(
            'core/language_expanded_search_table_layout.html'
        )

    @property
    def query_fieldset_list(self) -> Iterable:
        return [LangSearchFieldset(self.request_data.dict())]


def fav_remove(request):
    data = request.POST
    CofkUnionFavouriteLanguage.objects.filter(language_code=data['code_639_3']).delete()
    return JsonResponse({})


def fav_add(request):
    data = request.POST
    lang = get_object_or_404(Iso639LanguageCode, code_639_3=data['code_639_3'])
    CofkUnionFavouriteLanguage(language_code=lang).save()
    return JsonResponse({})
