from django import forms
from django.forms import ModelForm, HiddenInput, IntegerField, Form

from core.helper import form_utils
from core.helper import widgets_utils
from core.models import CofkUnionComment


def build_search_components(sort_by_choices: list[tuple[str, str]]):
    class SearchComponents(Form):
        template_name = 'core/form/search_components.html'
        sort_by = forms.CharField(label='Sort by',
                                  widget=forms.Select(choices=sort_by_choices),
                                  required=False, )

        num_record = forms.IntegerField(label='Records per page',
                                        widget=forms.Select(choices=[
                                            (5, 5),
                                            (25, 25),
                                            (50, 50),
                                            (100, 100),
                                        ]),
                                        required=False, )
        page = forms.IntegerField(widget=forms.HiddenInput())

    return SearchComponents


class RecrefForm(forms.Form):
    recref_id = forms.CharField(required=False, widget=forms.HiddenInput())
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())
    rec_name = forms.CharField(required=False)
    from_date = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    to_date = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    is_delete = form_utils.ZeroOneCheckboxField(required=False, is_str=False)


class CommentForm(ModelForm):
    comment_id = IntegerField(required=False, widget=HiddenInput())

    creation_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    creation_user = forms.CharField(required=False, widget=HiddenInput())
    change_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    change_user = forms.CharField(required=False, widget=HiddenInput())

    record_tracker_label = form_utils.record_tracker_label_fn_factory('Note')

    class Meta:
        model = CofkUnionComment
        fields = (
            'comment_id',
            'comment',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
        )
        labels = {
            'comment': 'Note',
        }
