# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import functools

from django.db import models
from django.db.models import OuterRef, CharField
from django.db.models.functions import Cast
from django.urls import reverse, resolve
from django.utils.http import urlencode

from core.form_label_maps import field_label_map
from core.helper import model_serv
from core.helper.model_serv import RecordTracker, ModelLike
from core.helper.url_serv import VNAME_SEARCH

SEQ_NAME_ISO_LANGUAGE__LANGUAGE_ID = 'iso_639_language_codes_id_seq'


class Recref(models.Model, RecordTracker):
    recref_id = models.AutoField(primary_key=True)
    from_date = models.DateField(null=True)
    to_date = models.DateField(null=True)

    relationship_type = models.CharField(max_length=100)

    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    class Meta:
        abstract = True


class CofkLookupDocumentType(models.Model):
    document_type_id = models.AutoField(primary_key=True)
    document_type_code = models.CharField(unique=True, max_length=3)
    document_type_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_lookup_document_type'


class CofkUnionComment(models.Model, RecordTracker):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_comment'


class CofkUnionNationality(models.Model):
    nationality_id = models.AutoField(primary_key=True)
    nationality_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_nationality'


class CofkUnionRelationshipType(models.Model, RecordTracker):
    relationship_code = models.CharField(primary_key=True, max_length=50)
    desc_left_to_right = models.CharField(max_length=200)
    desc_right_to_left = models.CharField(max_length=200)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    class Meta:
        db_table = 'cofk_union_relationship_type'


class CofkUnionResource(models.Model, RecordTracker):
    resource_id = models.AutoField(primary_key=True)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_resource'


class CofkUnionSpeedEntryText(models.Model):
    speed_entry_text_id = models.AutoField(primary_key=True)
    object_type = models.CharField(max_length=30)
    speed_entry_text = models.CharField(max_length=200)

    class Meta:
        db_table = 'cofk_union_speed_entry_text'


class CofkUnionImage(models.Model, RecordTracker):
    image_id = models.AutoField(primary_key=True)
    image_filename = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    thumbnail = models.TextField(blank=True, null=True)
    can_be_displayed = models.CharField(max_length=1)
    display_order = models.IntegerField(default=1)
    licence_details = models.TextField()
    licence_url = models.CharField(max_length=2000)
    credits = models.CharField(max_length=2000)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_image'


class CofkUnionOrgType(models.Model):
    org_type_id = models.AutoField(primary_key=True)
    org_type_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_org_type'


class CofkUnionRoleCategory(models.Model):
    role_category_id = models.AutoField(primary_key=True)
    role_category_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_role_category'
        ordering = ['role_category_desc']


class CofkUnionSubject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_subject'


class Iso639LanguageCode(models.Model):
    code_639_3 = models.CharField(max_length=3, primary_key=True)
    code_639_1 = models.CharField(max_length=2)
    language_name = models.CharField(max_length=100)
    language_id = models.IntegerField(
        default=functools.partial(model_serv.next_seq_safe, SEQ_NAME_ISO_LANGUAGE__LANGUAGE_ID),
        unique=True,
    )

    def __str__(self):
        return self.language_name

    class Meta:
        db_table = 'iso_639_language_codes'


class CofkUnionFavouriteLanguage(models.Model):
    language_code = models.OneToOneField(Iso639LanguageCode,
                                         models.CASCADE,
                                         db_column='language_code',
                                         primary_key=True)

    class Meta:
        db_table = 'cofk_union_favourite_language'


class CofkLookupCatalogue(models.Model):
    catalogue_id = models.AutoField(primary_key=True)
    catalogue_code = models.CharField(unique=True, max_length=100)
    catalogue_name = models.CharField(unique=True, max_length=500)
    is_in_union = models.IntegerField()
    publish_status = models.SmallIntegerField()

    class Meta:
        db_table = 'cofk_lookup_catalogue'
        ordering = ['catalogue_name']


def get_sort_by_label(url: str, query_order_by: str, pk) -> str:
    view = resolve(url).func.view_class()
    label = [c[1] for c in view.sort_by_choices if c[0] == query_order_by]

    if label:
        return label[0]


class CofkUserSavedQuery(models.Model):
    query_id = models.AutoField(primary_key=True)
    username = models.ForeignKey('login.CofkUser', models.DO_NOTHING, db_column='username')
    query_class = models.CharField(max_length=100)
    query_method = models.CharField(max_length=100)  # what does this do?
    query_title = models.TextField()  # this field is not used atm, instead use the dynamic property title
    query_order_by = models.CharField(max_length=100)
    query_sort_descending = models.SmallIntegerField()
    query_entries_per_page = models.SmallIntegerField()
    query_record_layout = models.CharField(max_length=12)
    query_menu_item_name = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)

    @property
    def base_url(self) -> str | None:
        if self.query_class == 'contributor' or self.query_class == 'language':
            return

        if 'work' in self.query_class:
            return reverse(f'work:{VNAME_SEARCH}')
        elif 'repository' == self.query_class:
            return reverse(f'institution:{VNAME_SEARCH}')
        elif 'audit_trail' == self.query_class:
            return reverse(f'audit:{VNAME_SEARCH}')
        elif 'uploader' == self.query_class:
            return reverse('uploader:upload_works')

        return reverse(f'{self.query_class}:{VNAME_SEARCH}')

    @property
    def title(self):
        title = 'Selection: '

        if self.query_class in field_label_map:
            ref = field_label_map[self.query_class]
            selections = [f'{ref[s.column_name]} {s.op_value} "{s.column_value}". ' for s in self.selection.all()]
        else:
            selections = [f'{s.column_name} {s.op_value} "{s.column_value}". ' for s in self.selection.all()]

        if len(selections) == 0:
            title += 'all. '
        else:
            title += ''.join(selections)

        if query_order_by := get_sort_by_label(self.base_url, self.query_order_by, self.pk):
            title += f'Data is sorted by: {query_order_by}'
        else:
            title += f'Data is sorted by: {self.query_order_by}'

        if self.query_sort_descending == 1:
            title += ' (descending order)'

        title += f'. Entries per page: {self.query_entries_per_page}.'

        return title

    @property
    def url(self):
        params = {'sort_by': self.query_order_by,
                  'num_record': self.query_entries_per_page}

        if self.query_sort_descending:
            params['order'] = 'desc'

        for selection in self.selection.all():
            params = params | {f'{selection.column_name}_lookup': selection.op_value,
                               selection.column_name: selection.column_value}

        return self.base_url + '?' + urlencode(params)

    class Meta:
        db_table = 'cofk_user_saved_queries'
        ordering = ['-creation_timestamp']


class CofkUserSavedQuerySelection(models.Model):
    selection_id = models.AutoField(primary_key=True)
    query = models.ForeignKey(CofkUserSavedQuery, models.CASCADE, related_name='selection')
    column_name = models.CharField(max_length=100)
    column_value = models.CharField(max_length=500)
    op_name = models.CharField(max_length=100)
    op_value = models.CharField(max_length=100)
    column_value2 = models.CharField(max_length=500)

    class Meta:
        db_table = 'cofk_user_saved_query_selection'


class MergeHistoryQuerySet(models.QuerySet):

    def get_by_new_model(self, new_model: ModelLike):
        return self.filter(new_id=str(new_model.pk), model_class_name=new_model.__class__.__name__)

    def subquery_new_id(self, model_class_name):
        return (self.filter(old_id=Cast(OuterRef('pk'), output_field=CharField()),
                            model_class_name=model_class_name)
                .values('new_id')[:1])


class MergeHistory(models.Model, RecordTracker):
    merge_history_id = models.AutoField(primary_key=True)

    new_id = models.CharField(max_length=250)
    new_display_id = models.CharField(max_length=250)
    new_name = models.TextField()

    old_id = models.CharField(max_length=250)
    old_display_id = models.CharField(max_length=250)
    old_name = models.TextField()

    model_class_name = models.CharField(max_length=200)

    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    objects = MergeHistoryQuerySet.as_manager()

    class Meta:
        db_table = 'merge_history'
        indexes = [
            models.Index(fields=['model_class_name', 'new_id']),
        ]
