import logging
from typing import Iterable

from django import forms
from django.db.models import TextChoices, Model
from django.forms import ModelForm, CharField
from django.forms.utils import ErrorList

from core import constant
from core.form_label_maps import field_label_map
from core.helper import form_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.form_utils import TargetPersonMRRForm, LocationRecrefField, BasicSearchFieldset, SearchCharField, \
    SearchIntField
from person.models import CofkUnionPerson
from person.recref_adapter import ActivePersonRecrefAdapter
from core.models import CofkUnionOrgType, CofkUnionRoleCategory

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

search_gender_choices = [
            (None, 'Any'),
            ('M', 'Male'),
            ('F', 'Female'),
            ('U', 'Unknown or not applicable'),
        ]

search_person_or_group = [
        (None, 'Either'),
        ('P', 'Person'),
        ('G', 'Group'),
    ]

class GeneralSearchFieldset(BasicSearchFieldset):
    role_category_names = CofkUnionRoleCategory.objects \
        .order_by('role_category_desc').values_list('role_category_desc', flat=True).distinct()

    title = 'General'
    template_name = 'person/component/person_search_fieldset.html'

    names_and_titles = SearchCharField(label=field_label_map['person']['names_and_titles'],
                                help_text="Primary name normally in 'surname, forename' format, followed by "
                                          "alternative names and titles or roles/professions. Roles and professions "
                                          "may have been entered as free text and/or as a list of standard categories "
                                          "(see below):")
    names_and_titles_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    birth_year_from = form_utils.create_year_field()
    birth_year_to = form_utils.create_year_field()
    birth_year_info = 'Can be entered in YYYY format. (In the case of organisations, ' \
                      'this field may hold the date of formation.)'

    death_year_from = form_utils.create_year_field()
    death_year_to = form_utils.create_year_field()
    death_year_info = 'Can be entered in YYYY format. (In the case of organisations, ' \
                      'this field may hold the date of dissolution.)'

    flourished_year_from = form_utils.create_year_field()
    flourished_year_to = form_utils.create_year_field()
    flourished_info = 'Can be entered in YYYY format.'

    gender = SearchCharField(widget=forms.Select(choices=search_gender_choices))

    person_or_group = SearchCharField(widget=forms.Select(choices=search_person_or_group))

    sent = SearchIntField(help_text="Number of letters from this author/sender. "
                                  "You can search on these 'number' fields using 'Advanced Search', "
                                  "e.g. you could enter something like 'Sent greater than 100' to "
                                  "identify the more prolific authors.")
    sent_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    recd = SearchIntField(label=field_label_map['person']['recd'], help_text='Number of letters sent to this addressee.')
    recd_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    all_works = SearchIntField(label=field_label_map['person']['all_works'],
                             help_text='Total of letters to and from this person/organisation.')
    all_works_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    mentioned = SearchIntField(help_text='Number of letters in which this person/organisation was mentioned.')
    mentioned_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    roles = SearchCharField(label=field_label_map['person']['roles'],
                            help_text='Also known as Professional categories.')
    roles_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    editors_notes = SearchCharField(label=field_label_map['person']['editors_notes'],
                                    help_text='Notes for internal use, intended to hold temporary queries etc.')
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    further_reading = SearchCharField()
    further_reading_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    images = SearchCharField()
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    other_details = SearchCharField(help_text='Summary of any other information about the person or group, '
                                              'including membership of organisations, known geographical '
                                              'locations, researchers\' notes and related resources.')
    other_details_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    iperson_id = SearchIntField(label=field_label_map['person']['iperson_id'],
                                help_text='The unique ID for the record within this database.')
    iperson_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)


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
