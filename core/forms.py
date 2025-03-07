from django import forms
from django.conf import settings
from django.forms import ModelForm, HiddenInput, IntegerField, Form
from django.urls import reverse

from core.helper import form_serv, model_serv
from core.helper import widgets_serv
from core.helper.form_serv import CommonTextareaField, ZeroOneCheckboxField
from core.models import CofkUnionComment, CofkUnionResource, CofkUnionImage, CofkLookupCatalogue, CofkUnionRoleCategory, \
    CofkUnionSubject, CofkUnionOrgType
from login.models import CofkUser
from login import utils
from manifestation.models import CofkUnionManifestation
from person import person_serv
from work import work_serv


class RecrefForm(forms.Form):
    recref_id = forms.CharField(required=False, widget=forms.HiddenInput())
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())
    rec_name = forms.CharField(required=False)
    from_date = forms.DateField(required=False, widget=widgets_serv.NewDateInput())
    to_date = forms.DateField(required=False, widget=widgets_serv.NewDateInput())
    is_delete = form_serv.DeleteCheckboxField()

    @property
    def target_url(self) -> str:
        return ''  # tobe define by subclass


class PersonRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return person_serv.get_checked_form_url_by_pk(self.initial.get('target_id'))


class LocRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return reverse('location:full_form', args=[self.initial.get('target_id')])


class WorkRecrefForm(RecrefForm):
    @property
    def target_url(self) -> str:
        return work_serv.get_checked_form_url_by_pk(self.initial.get('target_id'))


class ManifRecrefForm(RecrefForm):

    @property
    def target_url(self) -> str:
        manif_id = self.initial.get('target_id')
        if not manif_id:
            return ''

        manif: CofkUnionManifestation = model_serv.get_safe(CofkUnionManifestation, pk=manif_id)
        if not manif:
            return ''

        return reverse('work:manif_update', args=[manif.work.iwork_id, manif_id])


class CommentForm(ModelForm):
    comment_id = IntegerField(required=False, widget=HiddenInput())

    record_tracker_label = form_serv.record_tracker_label_fn_factory('Note')

    comment = form_serv.CommonTextareaField(required=True)

    is_delete = form_serv.DeleteCheckboxField()

    class Meta:
        model = CofkUnionComment
        fields = (
            'comment_id',
            'comment',
        )
        labels = {
            'comment': 'Note',
        }


class ResourceForm(ModelForm):
    resource_id = IntegerField(required=False, widget=HiddenInput())
    resource_url = forms.CharField(required=True,
                                   label='URL')
    resource_url.widget.attrs.update({'class': 'url_checker'})

    resource_name = forms.CharField(required=True,
                                    label='Title or brief description',
                                    widget=forms.TextInput(
                                        {'class': 'res_standtext'}
                                    ), )

    resource_details = CommonTextareaField(required=False, label='Further details of resource')
    resource_details.widget.attrs.update({'class': 'res_standtext'})

    record_tracker_label = form_serv.record_tracker_label_fn_factory('Entry')

    is_delete = ZeroOneCheckboxField(is_str=False, label='Delete')
    is_delete.widget.attrs.update({'class': 'warn-checked'})

    class Meta:
        model = CofkUnionResource
        fields = (
            # upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
            'resource_id',
            'resource_name',
            'resource_url',
            'resource_details',
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
    licence_details = form_serv.CommonTextareaField(label='Either: full text of licence*')

    licence_url = forms.CharField(required=False,
                                  label='licence URL*',
                                  initial=settings.DEFAULT_IMG_LICENCE_URL,
                                  )
    licence_url.widget.attrs.update({'class': 'url_checker', })

    can_be_displayed = form_serv.ZeroOneCheckboxField(required=False,
                                                       label='Can be displayed to public',
                                                       initial='1', )
    display_order = forms.IntegerField(required=False, label='Order for display in front end', initial=1)

    def clean_display_order(self):
        display_order = self.cleaned_data.get('display_order')
        try:
            return int(display_order)
        except:
            raise forms.ValidationError('Display order must be an integer')

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


class CatalogueForm(ModelForm):
    catalogue_name = forms.CharField(label="Description")
    catalogue_code = forms.CharField(label="Code")
    publish_status = form_serv.ZeroOneCheckboxField(required=False, label='Publish', initial='1', )
    owner = forms.ModelChoiceField(
        label="Owner",
        queryset=utils.get_contributing_editors(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="Select Owner"  # placeholder
    )

    class Meta:
        model = CofkLookupCatalogue
        fields = '__all__'


class RoleForm(ModelForm):
    role_category_desc = forms.CharField(label="Description")

    class Meta:
        model = CofkUnionRoleCategory
        fields = '__all__'


class SubjectForm(ModelForm):
    subject_desc = forms.CharField(label="Description")

    class Meta:
        model = CofkUnionSubject
        fields = '__all__'


class OrgTypeForm(ModelForm):
    org_type_desc = forms.CharField(label="Description")

    class Meta:
        model = CofkUnionOrgType
        fields = '__all__'
