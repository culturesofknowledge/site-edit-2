from typing import Callable, Iterable

from django.forms import ModelForm
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

from core.forms import CommentForm
from core.helper import renderer_utils, view_utils, model_utils
from core.helper.view_utils import CommonInitFormViewTemplate, DefaultSearchView
from publication.forms import PublicationForm
from publication.models import CofkUnionPublication


class PubSearchView(DefaultSearchView):

    @property
    def title(self) -> str:
        return 'Publication'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def merge_page_vname(self) -> str:
        return 'publication:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'publication:return_quick_init'

    def get_queryset(self):
        # KTODO
        queryset = CofkUnionPublication.objects.all()
        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('publication/search_table_layout.html')


class PubInitView(CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'publication/init_form.html', {'pub_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('publication:search')

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return PublicationForm


def full_form(request, pk):
    # KTODO
    pub = get_object_or_404(CofkUnionPublication, pk=pk)
    pub_form = PublicationForm(request.POST or None, instance=pub)

    def _render_form():
        return render(request, 'publication/init_form.html', {
            'pub_form': pub_form,
        })

    if request.POST:
        if not pub_form.is_valid():
            return _render_form()

        pub_form.save()
        return redirect('publication:search')

    return _render_form()


class PubQuickInitView(PubInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('publication:return_quick_init', new_instance.pk)


def return_quick_init(request, pk):
    pub = CofkUnionPublication.objects.get(pk=pk)
    return render(request, 'publication/return_quick_init_pub.html', {
        'pub': pub,
    })
