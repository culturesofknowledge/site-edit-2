from abc import ABC

from django import forms
from django.db import models
from django.forms import ModelForm, CharField
from django.test import TestCase

from core import constant
from core.constant import REL_TYPE_COMMENT_REFERS_TO
from core.forms import CommentForm, PersonRecrefForm
from core.helper.recref_handler import MultiRecrefAdapterHandler
from core.helper.view_handler import FullFormHandler
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from person.recref_adapter import ActivePersonRecrefAdapter, PassivePersonRecrefAdapter
from person.views import PersonCommentFormsetHandler, PersonResourceFormsetHandler, PersonImageRecrefHandler


class DumpLocationForm(ModelForm):
    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs=dict(readonly=True)),
                              label='Full name of location'

                              )

    def clean_location_name(self):
        location_name = self.cleaned_data.get('location_name')
        if location_name == 'invalid_location_name':
            raise forms.ValidationError('invalid location name')
        return location_name

    class Meta:
        model = CofkUnionLocation
        fields = (
            'location_name',
        )


class DumpPersonForm(ModelForm):
    foaf_name = models.CharField(max_length=200)

    class Meta:
        model = CofkUnionPerson
        fields = (
            'foaf_name',
        )


class DumpFullFormHandler(FullFormHandler):

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.location_form = DumpLocationForm(
            data={'location_name': 'old'},
            instance=CofkUnionLocation(location_name='old'),
        )
        self.person_form = DumpPersonForm(
            data={'foaf_name': 'old person'},
            instance=CofkUnionPerson(foaf_name='old person'),
        )


class DumpComplexFullFormHandler(FullFormHandler):
    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.person = CofkUnionPerson(foaf_name='old person')
        self.location_form = DumpLocationForm(
            data={'location_name': 'old'},
            instance=CofkUnionLocation(location_name='old'),
        )
        self.person_form = DumpPersonForm(
            data={'foaf_name': 'old person'},
            instance=self.person,
        )
        self.org_handler = MultiRecrefAdapterHandler(
            request_data, name='organisation',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )
        self.member_handler = MultiRecrefAdapterHandler(
            request_data, name='member',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )

        self.add_recref_formset_handler(PersonCommentFormsetHandler(
            prefix='comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_REFERS_TO,
            parent=self.person,
        ))

        self.add_recref_formset_handler(PersonResourceFormsetHandler(
            request_data=request_data,
            parent=self.person,
        ))
        self.img_recref_handler = PersonImageRecrefHandler(request_data, request and request.FILES,
                                                           parent=self.person,

                                                           )


class BasicFullFormHandlerTest(TestCase, ABC):
    def setUp(self):
        super().setUp()
        self.ffh = self.build_ffh()

    def build_ffh(self) -> DumpComplexFullFormHandler | DumpFullFormHandler:
        raise NotImplementedError()

    def run_test_prepare_cleaned_data(self):
        with self.assertRaises(AttributeError):
            self.ffh.location_form.cleaned_data

        self.ffh.prepare_cleaned_data()
        self.assertEqual(self.ffh.location_form.cleaned_data, {'location_name': 'old'})

    def run_test_is_any_changed(self):
        self.assertFalse(self.ffh.is_any_changed())
        self.ffh.location_form = DumpLocationForm({'location_name': 'new'},
                                                  instance=CofkUnionLocation(location_name='old'))
        self.assertTrue(self.ffh.is_any_changed())

    def run_test_is_invalid(self):
        self.assertFalse(self.ffh.is_invalid())
        self.ffh.location_form = DumpLocationForm({'location_name': 'invalid_location_name'},
                                                  instance=CofkUnionLocation(location_name='old'))
        self.assertTrue(self.ffh.is_invalid())


class SimpleFullFormHandlerTest(BasicFullFormHandlerTest):
    """
    test DumpFullFormHandler that only have simple form
    """

    def build_ffh(self):
        return DumpFullFormHandler(pk=9999)

    def test_every_form_formset(self):
        formset = list(self.ffh.every_form_formset)
        self.assertEqual(formset, [self.ffh.location_form, self.ffh.person_form])

    def test_create_context(self):
        self.assertEqual(
            self.ffh.create_context(),
            {
                'location_form': self.ffh.location_form,
                'person_form': self.ffh.person_form,
            }
        )

    def test_all_named_form_formset(self):
        named_form_formset = list(self.ffh.all_named_form_formset())
        self.assertEqual(named_form_formset, [
            ('location_form', self.ffh.location_form),
            ('person_form', self.ffh.person_form),
        ])

    def test_is_any_changed(self):
        self.run_test_is_any_changed()

    def test_is_invalid(self):
        self.run_test_is_invalid()

    def test_prepare_cleaned_data(self):
        self.run_test_prepare_cleaned_data()


class ComplexFullFormHandlerTest(BasicFullFormHandlerTest):
    """
    test DumpComplexFullFormHandler that have multiple form and formset
    """

    def build_ffh(self):

        request_data = {
            'image-TOTAL_FORMS': ['1'], 'image-INITIAL_FORMS': ['0'], 'image-MIN_NUM_FORMS': ['0'],
            'image-MAX_NUM_FORMS': ['1000'], 'selected_image': [''], 'image-0-image_id': [''],
            'image-0-image_filename': [''], 'image-0-thumbnail': [''], 'image-0-credits': [''],
            'image-0-licence_details': [''],
            'image-0-licence_url': ['http://cofk2.bodleian.ox.ac.uk/culturesofknowledge/licence/terms_of_use.html'],
            'image-0-can_be_displayed': ['1'], 'image-0-display_order': ['1']
        }
        return DumpComplexFullFormHandler(pk=9999, request_data=request_data,)

    def test_all_named_form_formset(self):
        self.assertEqual(
            set(h for _, h in self.ffh.all_named_form_formset()),
            {
                self.ffh.location_form,
                self.ffh.person_form,
            }
        )

    def test_all_img_recref_handlers(self):
        self.assertEqual(
            set(self.ffh.all_img_recref_handlers()),
            {
                ('img_recref_handler', self.ffh.img_recref_handler),
            }
        )

    def test_all_recref_handlers(self):
        self.assertEqual(
            set(self.ffh.all_recref_handlers),
            {
                self.ffh.org_handler,
                self.ffh.member_handler,
            }
        )

    def test_every_form_formset(self):
        every_form_formset = set(self.ffh.every_form_formset)
        recref_formset = {h.formset for h in self.ffh.all_recref_formset_handlers()}
        self.assertEqual(recref_formset & every_form_formset, recref_formset)
        self.assertIn(self.ffh.location_form, every_form_formset)
        self.assertIn(self.ffh.person_form, every_form_formset)
        self.assertIn(self.ffh.img_recref_handler.formset, every_form_formset)
        self.assertIn(self.ffh.org_handler.new_form, every_form_formset)
        self.assertIn(self.ffh.org_handler.update_formset, every_form_formset)

    def test_create_context(self):
        print(self.ffh.create_context())
        expected_context = ({
                                'location_form': self.ffh.location_form,
                                'person_form': self.ffh.person_form,
                            } | self.ffh.img_recref_handler.create_context()
                            | self.ffh.org_handler.create_context()
                            | self.ffh.member_handler.create_context()
                            )
        for v in self.ffh.recref_formset_handlers:
            expected_context |= v.create_context()

        self.assertDictEqual(self.ffh.create_context(), expected_context)

    def test_is_any_changed(self):
        self.run_test_is_any_changed()

    def test_is_invalid(self):
        self.run_test_is_invalid()

    def test_prepare_cleaned_data(self):
        self.run_test_prepare_cleaned_data()
