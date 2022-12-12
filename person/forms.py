import logging
from typing import Iterable

from django import forms
from django.db.models import TextChoices, Model
from django.forms import ModelForm, CharField
from django.forms.utils import ErrorList

from core import constant
from core.helper import form_utils, widgets_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.form_utils import TargetPersonMRRForm, LocationRecrefField
from person.models import CofkUnionPerson
from person.recref_adapter import ActivePersonRecrefAdapter
from uploader.models import CofkUnionOrgType

log = logging.getLogger(__name__)

calendar_date_choices = [
    ("", 'Unknown'),
    ("G", 'Gregorian'),
    ("JM", 'Julian (year starting 25th Mar)'),
    ("JJ", 'Julian (year starting 1st Jan)'),
    ("O", 'Other'),
]

person_gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('', 'Unknown or not applicable'),
]


class YesEmptyCheckboxField(forms.CharField):
    def __init__(self, *args, **kwargs):
        widget = forms.CheckboxInput({'class': 'elcheckbox'},
                                     check_test=lambda v: v == 'Y')
        default_kwargs = dict(
            widget=widget,
            initial='',
            required=False,
        )
        kwargs = default_kwargs | kwargs
        super().__init__(*args, **kwargs)

    def clean(self, value):
        new_value = super().clean(value)
        return 'Y' if new_value == 'True' else ''


class OrgTypeField(forms.IntegerField):
    def __init__(self, **kwargs):
        widget = forms.Select()
        super().__init__(widget=widget, **kwargs)

    def reload_choices(self):
        self.widget.choices = [
            (None, ''),
            *self.find_org_type_choices()
        ]

    def find_org_type_choices(self) -> Iterable[tuple[int, str]]:
        for o in CofkUnionOrgType.objects.iterator():
            yield o.org_type_id, o.org_type_desc

    def clean(self, value):
        org_type_id = super().clean(value)
        if org_type_id is not None:
            return CofkUnionOrgType.objects.get(pk=org_type_id)
        return org_type_id


class PersonForm(ModelForm):
    gender = CharField(required=False,
                       widget=forms.RadioSelect(choices=person_gender_choices))

    is_organisation = YesEmptyCheckboxField()
    roles_titles = forms.CharField(required=False,
                                   widget=forms.CheckboxSelectMultiple(
                                       choices=[
                                           ('5', 'Antiquary'),
                                           ('28', 'Astrologer'),
                                           ('1', 'Astronomer'),
                                           ('8', 'Biographer'),
                                           ('15', 'Bookseller'),
                                           ('17', 'Classicist'),
                                           ('3', 'Cleric'),
                                           ('19', 'Diplomat'),
                                           ('10', 'Educational Theorist'),
                                           ('26', 'Freemason'),
                                           ('20', 'Keeper'),
                                           ('18', 'Lawyer'),
                                           ('24', 'Letter Carrier'),
                                           ('12', 'Linguist'),
                                           ('6', 'Mathematician'),
                                           ('16', 'Merchant'),
                                           ('22', 'Musician'),
                                           ('7', 'Natural Historian'),
                                           ('9', 'Naturalist'),
                                           ('23', 'Nonjuror'),
                                           ('27', 'Philosopher'),
                                           ('13', 'Physician'),
                                           ('2', 'Politician'),
                                           ('25', 'Printer'),
                                           ('14', 'Scholar'),
                                           ('21', 'Soldier'),
                                           ('4', 'Theologian'),
                                           ('11', 'Writer'),
                                       ]
                                   )
                                   )

    date_of_birth_year = form_utils.create_year_field()
    date_of_birth_month = form_utils.create_month_field()
    date_of_birth_day = form_utils.create_day_field()
    date_of_birth2_year = form_utils.create_year_field()
    date_of_birth2_month = form_utils.create_month_field()
    date_of_birth2_day = form_utils.create_day_field()
    date_of_birth_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    date_of_death_year = form_utils.create_year_field()
    date_of_death_month = form_utils.create_month_field()
    date_of_death_day = form_utils.create_day_field()
    date_of_death2_year = form_utils.create_year_field()
    date_of_death2_month = form_utils.create_month_field()
    date_of_death2_day = form_utils.create_day_field()
    date_of_death_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    flourished_year = form_utils.create_year_field()
    flourished_month = form_utils.create_month_field()
    flourished_day = form_utils.create_day_field()
    flourished2_year = form_utils.create_year_field()
    flourished2_month = form_utils.create_month_field()
    flourished2_day = form_utils.create_day_field()
    flourished_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_calendar = forms.CharField(required=False,
                                          widget=forms.RadioSelect(choices=calendar_date_choices, ))

    organisation_type = OrgTypeField(required=False)

    # extra field
    birth_place = LocationRecrefField(required=False)
    death_place = LocationRecrefField(required=False)
    other_place = forms.CharField(required=False, widget=forms.HiddenInput())
    selected_other_id = forms.CharField(required=False)

    def __init__(self, data=None, files=None, auto_id="id_%s", prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        self.is_org_form = False

    class Meta:
        model = CofkUnionPerson
        fields = (
            'foaf_name',
            'gender',
            'is_organisation',
            'editors_notes',
            'skos_altlabel',
            'person_aliases',

            'date_of_birth_year',
            'date_of_birth_month',
            'date_of_birth_day',
            'date_of_birth2_year',
            'date_of_birth2_month',
            'date_of_birth2_day',
            'date_of_birth',
            'date_of_birth_inferred',
            'date_of_birth_uncertain',
            'date_of_birth_approx',
            'date_of_birth_calendar',

            'date_of_death_year',
            'date_of_death_month',
            'date_of_death_day',
            'date_of_death2_year',
            'date_of_death2_month',
            'date_of_death2_day',
            'date_of_death',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',

            'flourished_year',
            'flourished_month',
            'flourished_day',
            'flourished2_year',
            'flourished2_month',
            'flourished2_day',
            'flourished',
            'flourished_inferred',
            'flourished_uncertain',
            'flourished_approx',

            'further_reading',

            'date_of_birth_is_range',
            'date_of_death_is_range',
            'flourished_is_range',

            'organisation_type',

        )

    def clean(self):
        log.debug(f'cleaned_data: {self.cleaned_data}')
        form_utils.clean_by_default_value(self.cleaned_data, [
            'date_of_birth_inferred',
            'date_of_birth_uncertain',
            'date_of_birth_approx',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',
            'flourished_inferred',
            'flourished_uncertain',
            'flourished_approx',

            'date_of_birth_is_range',
            'date_of_death_is_range',
            'flourished_is_range',
        ], 0)

        return super().clean()


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'person/component/person_search_fieldset.html'

    iperson_id = forms.IntegerField(required=False)
    iperson_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    foaf_name = forms.CharField(required=False)
    foaf_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    birth_year_from = form_utils.create_year_field()
    birth_year_to = form_utils.create_year_field()

    death_year_from = form_utils.create_year_field()
    death_year_to = form_utils.create_year_field()

    flourished_year_from = form_utils.create_year_field()
    flourished_year_to = form_utils.create_year_field()

    gender = forms.CharField(required=False, widget=forms.Select(
        choices=[
            (None, 'All'),
            ('M', 'Male'),
            ('F', 'Female'),
            ('U', 'Unknown or not applicable'),
        ]
    ))

    person_or_group = forms.CharField(required=False, widget=forms.Select(choices=[
        (None, 'All'),
        ('P', 'Person'),
        ('G', 'Group'),
    ]))

    editors_notes = forms.CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    further_reading = forms.CharField(required=False)
    further_reading_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_timestamp_from = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    change_timestamp_to = forms.DateField(required=False, widget=widgets_utils.NewDateInput())

    change_user = forms.CharField(required=False)
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)


class PersonOtherRelationChoices(TextChoices):
    UNSPECIFIED_RELATIONSHIP_WITH = constant.REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH, 'Unspecified Relationship With'
    ACQUAINTANCE_OF = constant.REL_TYPE_ACQUAINTANCE_OF, 'Acquaintance Of'
    WAS_BUSINESS_ASSOCIATE = constant.REL_TYPE_WAS_BUSINESS_ASSOCIATE, 'Was A Business Associate Of'
    COLLABORATED_WITH = constant.REL_TYPE_COLLABORATED_WITH, 'Collaborated With'
    COLLEAGUE_OF = constant.REL_TYPE_COLLEAGUE_OF, 'Colleague Of'
    FRIEND_OF = constant.REL_TYPE_FRIEND_OF, 'Friend Of'
    RELATIVE_OF = constant.REL_TYPE_RELATIVE_OF, 'Relative Of'
    SIBLING_OF = constant.REL_TYPE_SIBLING_OF, 'Sibling Of'
    SPOUSE_OF = constant.REL_TYPE_SPOUSE_OF, 'Spouse Of'


class PersonOtherRecrefForm(TargetPersonMRRForm):
    no_date = False
    relationship_types = PersonOtherRelationChoices

    @classmethod
    def create_recref_adapter(cls, *args, **kwargs) -> RecrefFormAdapter:
        return ActivePersonRecrefAdapter(*args, **kwargs)

    def find_recref_list_by_target_id(self, parent: Model, target_id):
        parent: CofkUnionPerson
        return parent.active_relationships.filter(
            person_id=target_id,
            relationship_type__in=self.get_rel_type_choices_values(),
        )
