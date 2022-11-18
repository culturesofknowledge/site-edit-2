from django import forms
from django.conf import settings
from django.forms import ModelForm, HiddenInput, IntegerField, Form
from django.urls import reverse

from core.helper import form_utils, model_utils
from core.helper import widgets_utils
from core.models import CofkUnionComment, CofkUnionResource
from manifestation.models import CofkUnionManifestation
from person import person_utils
from uploader.models import CofkUnionImage
from work import work_utils


def build_search_components(sort_by_choices: list[tuple[str, str]]):
    class SearchComponents(Form):
        template_name = 'core/form/search_components.html'
        sort_by = forms.CharField(label='Sort by',
                                  widget=forms.Select(choices=sort_by_choices),
                                  required=False, )

        num_record = forms.IntegerField(label='Records per page',
                                        widget=forms.Select(choices=[
                                            (10, 10),
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

    @property
    def target_url(self) -> str:
        return ''  # tobe define by subclass


class PersonRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return person_utils.get_checked_form_url_by_pk(self.initial.get('target_id'))


class LocRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return reverse('location:full_form', args=[self.initial.get('target_id')])


class WorkRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return work_utils.get_checked_form_url_by_pk(self.initial.get('target_id'))


class ManifRecrefForm(RecrefForm):

    @property
    def target_url(self) -> str:
        manif_id = self.initial.get('target_id')
        if not manif_id:
            return ''

        manif: CofkUnionManifestation = model_utils.get_safe(CofkUnionManifestation, pk=manif_id)
        if not manif:
            return ''

        return reverse('work:manif_update', args=[manif.work.iwork_id, manif_id])


class CommentForm(ModelForm):
    comment_id = IntegerField(required=False, widget=HiddenInput())

    creation_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    creation_user = forms.CharField(required=False, widget=HiddenInput())
    change_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    change_user = forms.CharField(required=False, widget=HiddenInput())

    record_tracker_label = form_utils.record_tracker_label_fn_factory('Note')

    comment = form_utils.CommonTextareaField(required=True)

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


class ResourceForm(ModelForm):
    resource_id = IntegerField(required=False, widget=HiddenInput())
    resource_url = forms.CharField(required=False,
                                   label='URL')

    resource_url.widget.attrs.update({'class': 'url_checker'})
    resource_name = forms.CharField(required=True,
                                    label='Title or brief description',
                                    widget=forms.Textarea(
                                        {'class': 'res_standtext', 'rows': '4'}
                                    ), )

    resource_details = forms.CharField(required=True,
                                       label='Further details of resource',
                                       widget=forms.Textarea(
                                           {'class': 'res_standtext', 'rows': '4'}
                                       ), )

    creation_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    creation_user = forms.CharField(required=False, widget=HiddenInput())
    change_timestamp = forms.DateTimeField(required=False, widget=HiddenInput())
    change_user = forms.CharField(required=False, widget=HiddenInput())

    record_tracker_label = form_utils.record_tracker_label_fn_factory('Entry')

    class Meta:
        model = CofkUnionResource
        fields = (
            # upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
            'resource_id',
            'resource_name',
            'resource_url',
            'resource_details',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
        )


class ImageForm(ModelForm):
    image_id = IntegerField(required=False, widget=HiddenInput())
    image_filename = forms.CharField(required=False,
                                     label='URL for full-size image')
    image_filename.widget.attrs.update({'class': 'url_checker'})

    thumbnail = forms.CharField(required=False,
                                label='URL for thumbnail (if any)')
    credits = forms.CharField(required=False,
                              label="Credits for 'front end' display*")
    licence_details = form_utils.CommonTextareaField(label='Either: full text of licence*')

    licence_url = forms.CharField(required=False,
                                  label='licence URL*')
    licence_url.widget.attrs.update({'class': 'url_checker', 'value': settings.DEFAULT_IMG_LICENCE_URL})

    can_be_displayed = form_utils.ZeroOneCheckboxField(required=False,
                                                       label='Can be displayed to public',
                                                       initial='1', )
    display_order = forms.IntegerField(required=False, label='Order for display in front end')

    class Meta:
        model = CofkUnionImage
        fields = (
            'image_id',
            'image_filename',
            'thumbnail',
            'credits',
            'licence_details',
            'licence_url',
            'can_be_displayed',
            'display_order',
        )


class UploadImageForm(Form):
    selected_image = forms.ImageField(required=False)
