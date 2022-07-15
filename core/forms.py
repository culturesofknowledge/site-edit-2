from typing import Tuple, List

from django import forms
from django.forms import Form


def build_search_components(sort_by_choices: List[Tuple[str, str]]):
    class SearchComponents(Form):
        template_name = 'core/form/search_components.html'
        sort_by = forms.CharField(label='Sort by',
                                  widget=forms.Select(choices=sort_by_choices)
                                  )

        num_record = forms.IntegerField(label='Records per page',
                                        widget=forms.Select(choices=[
                                            (4, 4),
                                            (25, 25),
                                            (50, 50),
                                            (100, 100),
                                        ]))
        page = forms.IntegerField(widget=forms.HiddenInput())

    return SearchComponents
