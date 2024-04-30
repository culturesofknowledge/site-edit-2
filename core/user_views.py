from typing import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin

from core.helper import renderer_serv, query_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView
from core.user_forms import UserSearchFieldset
from login.models import CofkUser


class UserSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('username', 'User name',),
        ]

    @property
    def entity(self) -> str:
        return 'User,Users'

    # @property
    # def search_field_fn_maps(self) -> dict[str, Lookup]:
    #     return {
    #         'is_favorite': query_is_favorite,
    #     }

    @property
    def default_order(self) -> str:
        return 'asc'

    def get_queryset(self):
        model_class = CofkUser
        request_data = self.request_data.dict()
        if not request_data:
            return model_class.objects.none()


        queries = []
        queries.extend(
            query_serv.create_queries_by_lookup_field(request_data, self.search_fields,
                                                      search_fields_fn_maps={
                                                          'is_staff': query_serv.lookup_fn_true_false,
                                                          'is_active': query_serv.lookup_fn_true_false,
                                                      })
        )
        queryset = model_class.objects.filter()
        queryset = query_serv.update_queryset(queryset, model_class, queries=queries,
                                              sort_by=self.get_sort_by())
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer(
            'core/user_expanded_search_table_layout.html'
        )

    @property
    def query_fieldset_list(self) -> Iterable:
        return [UserSearchFieldset(self.request_data.dict())]
