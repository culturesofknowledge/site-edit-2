from django import forms
from django.forms import Form


class SearchComponents(Form):
    template_name = 'core/form/search_components.html'
    sort_by = forms.CharField(label='Sort by',
                              widget=forms.Select(choices=[('Desc', 'desc'),
                                                           ('Asc', 'asc')])
                              )

    num_record = forms.CharField(label='Records per page',
                                 widget=forms.Select(choices=[(25, 25),
                                                              (50, 50),
                                                              (100, 100),
                                                              ]))
