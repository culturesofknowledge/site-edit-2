import functools

from django.db import models
from django.utils.safestring import mark_safe

from core.helper import model_serv
from core.helper.model_serv import RecordTracker
from core.models import Recref

SEQ_NAME_COFKUNIONPERSION__IPERSON_ID = 'cofk_union_person_iperson_id_seq'


class CofkUnionPerson(models.Model, RecordTracker):
    person_id = models.CharField(primary_key=True, max_length=100)
    foaf_name = models.CharField(max_length=200)
    skos_altlabel = models.TextField(blank=True, null=True)  # Synonyms

    """
    'Other versions of name'
    who assign value and use this field ?
    """
    skos_hiddenlabel = models.TextField(blank=True, null=True)
    person_aliases = models.TextField(blank=True, null=True)  # Difference between synonyms and aliases?
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
        default=functools.partial(model_serv.next_seq_safe, SEQ_NAME_COFKUNIONPERSION__IPERSON_ID),
        unique=True,
    )
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    editors_notes = models.TextField(blank=True, null=True)
    further_reading = models.TextField(blank=True, null=True)
    organisation_type = models.ForeignKey('core.CofkUnionOrgType', models.DO_NOTHING, db_column='organisation_type',
                                          blank=True, null=True, related_name='person')
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
    locations = models.ManyToManyField(to='location.CofkUnionLocation',
                                       through='person.CofkPersonLocationMap',
                                       through_fields=('person', 'location'))
    images = models.ManyToManyField(to='core.CofkUnionImage',
                                    through='CofkPersonImageMap')
    resources = models.ManyToManyField(to='core.CofkUnionResource',
                                       through='CofkPersonResourceMap')
    comments = models.ManyToManyField(to='core.CofkUnionComment',
                                      through='CofkPersonCommentMap')
    works = models.ManyToManyField(to='work.CofkUnionWork',
                                   through='work.CofkWorkPersonMap')
    roles = models.ManyToManyField(to='core.CofkUnionRoleCategory',
                                   through='CofkPersonRoleMap', related_name='person')
    merged_master = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name='merged_sources')

    # related_people = models.ManyToManyField(to='CofkUnionPerson',
    #                                        through='CofkPersonPersonMap',
    #                                        through_fields=('person', 'related'))

    @property
    def names_and_roles(self) -> str:
        from person import person_serv
        names_and_roles = ''.join(f'<p>{s}</p>' for s in person_serv.get_name_details(self))
        return mark_safe(names_and_roles)

    def to_string(self, is_details=False) -> str:
        """
        Used by work.creators_for_display and work.addressees_for_display
        """
        dob = str(self.date_of_birth_year)
        dod = str(self.date_of_death_year)

        if self.date_of_death_is_range == 1:
            dod += ' or after'

        if self.date_of_birth_is_range == 1:
            dob += ' or before'

        if self.date_of_birth_year and self.date_of_death_year:
            person = f'{self.foaf_name}, {dob}-{dod}'
        elif self.date_of_birth_year:
            person = f'{self.foaf_name} b. {dob}'
        elif self.date_of_death_year:
            person = f'{self.foaf_name} d. {dod}'
        else:
            person = str(self.foaf_name)

        if not is_details:
            return person

        if self.skos_altlabel:
            person += f', also known as: {self.skos_altlabel}'

        if self.person_aliases:
            person += f' (titles/roles: {self.person_aliases}'

        return person

    class Meta:
        db_table = 'cofk_union_person'
        permissions = [
            ('export_file', 'Export csv/excel from search results'),
            ('clonefinder', 'Allow use clonefinder feature to find similar records'),
        ]
        indexes = [
            models.Index(fields=['iperson_id']),
        ]


class CofkPersonLocationMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    location = models.ForeignKey('location.CofkUnionLocation', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_location_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
        ]


class CofkPersonPersonMap(Recref):
    person = models.ForeignKey(CofkUnionPerson,
                               related_name='active_relationships',
                               on_delete=models.CASCADE)
    related = models.ForeignKey(CofkUnionPerson,
                                related_name='passive_relationships',
                                on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_person_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
            models.Index(fields=['related', 'relationship_type']),
        ]


class CofkPersonCommentMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_comment_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
        ]


class CofkPersonResourceMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_resource_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
        ]


class CofkPersonImageMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    image = models.ForeignKey('core.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_image_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
        ]


class CofkPersonRoleMap(Recref):
    person = models.ForeignKey(CofkUnionPerson, on_delete=models.CASCADE)
    role = models.ForeignKey('core.CofkUnionRoleCategory', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_person_role_map'
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
        ]


def create_person_id(iperson_id) -> str:
    return f'cofk_union_person-iperson_id:{iperson_id}'


