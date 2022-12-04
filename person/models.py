import functools

from django.db import models

from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref

SEQ_NAME_COFKUNIONPERSION__IPERSON_ID = 'cofk_union_person_iperson_id_seq'


class CofkCollectPerson(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    iperson_id = models.IntegerField(blank=True, null=True)
    # KTODO temporary related_name
    union_iperson = models.ForeignKey('CofkUnionPerson', models.DO_NOTHING, blank=True, null=True,
                                      related_name='union_collect_persons')
    person = models.ForeignKey('CofkUnionPerson', models.DO_NOTHING, blank=True, null=True,
                               related_name='collect_persons')
    primary_name = models.CharField(max_length=200)
    alternative_names = models.TextField(blank=True, null=True)
    roles_or_titles = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1)
    is_organisation = models.CharField(max_length=1)
    organisation_type = models.IntegerField(blank=True, null=True)
    date_of_birth_year = models.IntegerField(blank=True, null=True)
    date_of_birth_month = models.IntegerField(blank=True, null=True)
    date_of_birth_day = models.IntegerField(blank=True, null=True)
    date_of_birth_is_range = models.SmallIntegerField(default=0)
    date_of_birth2_year = models.IntegerField(blank=True, null=True)
    date_of_birth2_month = models.IntegerField(blank=True, null=True)
    date_of_birth2_day = models.IntegerField(blank=True, null=True)
    date_of_birth_inferred = models.SmallIntegerField(default=0)
    date_of_birth_uncertain = models.SmallIntegerField(default=0)
    date_of_birth_approx = models.SmallIntegerField(default=0)
    date_of_death_year = models.IntegerField(blank=True, null=True)
    date_of_death_month = models.IntegerField(blank=True, null=True)
    date_of_death_day = models.IntegerField(blank=True, null=True)
    date_of_death_is_range = models.SmallIntegerField(default=0)
    date_of_death2_year = models.IntegerField(blank=True, null=True)
    date_of_death2_month = models.IntegerField(blank=True, null=True)
    date_of_death2_day = models.IntegerField(blank=True, null=True)
    date_of_death_inferred = models.SmallIntegerField(default=0)
    date_of_death_uncertain = models.SmallIntegerField(default=0)
    date_of_death_approx = models.SmallIntegerField(default=0)
    flourished_year = models.IntegerField(blank=True, null=True)
    flourished_month = models.IntegerField(blank=True, null=True)
    flourished_day = models.IntegerField(blank=True, null=True)
    flourished_is_range = models.SmallIntegerField(default=0)
    flourished2_year = models.IntegerField(blank=True, null=True)
    flourished2_month = models.IntegerField(blank=True, null=True)
    flourished2_day = models.IntegerField(blank=True, null=True)
    notes_on_person = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_person'
        unique_together = (('upload', 'iperson_id'),)

    def __str__(self):
        return str(self.union_iperson) if self.union_iperson is not None else f'{self.primary_name} (collect)'


class CofkUnionPerson(models.Model, RecordTracker):
    person_id = models.CharField(primary_key=True, max_length=100)
    foaf_name = models.CharField(max_length=200)
    skos_altlabel = models.TextField(blank=True, null=True)
    skos_hiddenlabel = models.TextField(blank=True, null=True)
    person_aliases = models.TextField(blank=True, null=True)
    date_of_birth_year = models.IntegerField(blank=True, null=True)
    date_of_birth_month = models.IntegerField(blank=True, null=True)
    date_of_birth_day = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_birth_inferred = models.SmallIntegerField(default=0)
    date_of_birth_uncertain = models.SmallIntegerField(default=0)
    date_of_birth_approx = models.SmallIntegerField(default=0)
    date_of_death_year = models.IntegerField(blank=True, null=True)
    date_of_death_month = models.IntegerField(blank=True, null=True)
    date_of_death_day = models.IntegerField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)
    date_of_death_inferred = models.SmallIntegerField(default=0)
    date_of_death_uncertain = models.SmallIntegerField(default=0)
    date_of_death_approx = models.SmallIntegerField(default=0)
    gender = models.CharField(max_length=1)
    is_organisation = models.CharField(max_length=1)
    iperson_id = models.IntegerField(
        default=functools.partial(model_utils.next_seq_safe, SEQ_NAME_COFKUNIONPERSION__IPERSON_ID),
        unique=True,
    )
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    editors_notes = models.TextField(blank=True, null=True)
    further_reading = models.TextField(blank=True, null=True)
    organisation_type = models.ForeignKey('uploader.CofkUnionOrgType', models.DO_NOTHING, db_column='organisation_type',
                                          blank=True, null=True)
    date_of_birth_calendar = models.CharField(max_length=2)
    date_of_birth_is_range = models.SmallIntegerField(default=0)
    date_of_birth2_year = models.IntegerField(blank=True, null=True)
    date_of_birth2_month = models.IntegerField(blank=True, null=True)
    date_of_birth2_day = models.IntegerField(blank=True, null=True)
    date_of_death_calendar = models.CharField(max_length=2)
    date_of_death_is_range = models.SmallIntegerField(default=0)
    date_of_death2_year = models.IntegerField(blank=True, null=True)
    date_of_death2_month = models.IntegerField(blank=True, null=True)
    date_of_death2_day = models.IntegerField(blank=True, null=True)
    flourished = models.DateField(blank=True, null=True)
    flourished_calendar = models.CharField(max_length=2)
    flourished_is_range = models.SmallIntegerField(default=0)
    flourished_year = models.IntegerField(blank=True, null=True)
    flourished_month = models.IntegerField(blank=True, null=True)
    flourished_day = models.IntegerField(blank=True, null=True)
    flourished2_year = models.IntegerField(blank=True, null=True)
    flourished2_month = models.IntegerField(blank=True, null=True)
    flourished2_day = models.IntegerField(blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    flourished_inferred = models.SmallIntegerField(default=0)
    flourished_uncertain = models.SmallIntegerField(default=0)
    flourished_approx = models.SmallIntegerField(default=0)

    locations = models.ManyToManyField('location.CofkUnionLocation',
                                       through='person.CofkPersonLocationMap',
                                       through_fields=('person', 'location'))

    images = models.ManyToManyField('uploader.CofkUnionImage')

    @property
    def comments(self):
        return self.cofkpersoncommentmap_set.all()

    @property
    def resources(self):
        return self.cofkpersonresourcemap_set.all()

    class Meta:
        db_table = 'cofk_union_person'


class CofkPersonLocationMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    location = models.ForeignKey('location.CofkUnionLocation', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_location_map'


class CofkPersonPersonMap(Recref):
    person = models.ForeignKey(CofkUnionPerson,
                               related_name='active_relationships',
                               on_delete=models.CASCADE)
    related = models.ForeignKey(CofkUnionPerson,
                                related_name='passive_relationships',
                                on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_person_map'


class CofkPersonCommentMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_comment_map'


class CofkPersonResourceMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_resource_map'


class CofkPersonImageMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    image = models.ForeignKey('uploader.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_image_map'


class CofkPersonRoleMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    role = models.ForeignKey('uploader.CofkUnionRoleCategory', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_role_map'


class CofkCollectOccupationOfPerson(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    occupation_of_person_id = models.IntegerField()
    iperson_id = models.IntegerField()
    occupation = models.ForeignKey('uploader.CofkUnionRoleCategory', models.DO_NOTHING)

    class Meta:
        db_table = 'cofk_collect_occupation_of_person'
        unique_together = (('upload', 'occupation_of_person_id'),)


class CofkCollectPersonResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    iperson_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_person_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkUnionPersonSummary(models.Model):
    iperson = models.OneToOneField(CofkUnionPerson, models.DO_NOTHING, primary_key=True)
    other_details_summary = models.TextField(blank=True, null=True)
    other_details_summary_searchable = models.TextField(blank=True, null=True)
    sent = models.IntegerField()
    recd = models.IntegerField()
    all_works = models.IntegerField()
    mentioned = models.IntegerField()
    role_categories = models.TextField(blank=True, null=True)
    images = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_person_summary'


def create_person_id(iperson_id) -> str:
    return f'cofk_union_person-iperson_id:{iperson_id}'
