import logging
import os
import re
import time
from typing import Iterable
from zipfile import BadZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q, Lookup
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from core import constant
from core.form_label_maps import field_label_map
from core.helper.query_serv import create_from_to_datetime, create_queries_by_field_fn_maps, \
    create_queries_by_lookup_field
from core.helper.renderer_serv import create_table_search_results_renderer, RendererFactory
from core.helper.view_serv import DefaultSearchView
from core.models import CofkLookupCatalogue
from uploader.forms import CofkCollectUploadForm, GeneralSearchFieldset
from uploader.models import CofkCollectUpload, CofkCollectAddresseeOfWork, CofkCollectAuthorOfWork, \
    CofkCollectDestinationOfWork, CofkCollectLanguageOfWork, CofkCollectOriginOfWork, CofkCollectPersonMentionedInWork, \
    CofkCollectWorkResource, CofkCollectInstitution, CofkCollectLocation, CofkCollectManifestation, CofkCollectPerson, \
    CofkCollectSubjectOfWork
from uploader.review import accept_works, reject_works, get_work
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.uploader_serv import DisplayableCollectWork
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)


def handle_upload(request) -> dict:
    form = CofkCollectUploadForm(request.POST, request.FILES)
    report = {}

    if form.is_valid():
        start = time.time()
        new_upload = form.save(commit=False)
        new_upload.upload_status_id = 1
        new_upload.uploader_email = request.user.email
        new_upload.upload_timestamp = timezone.now()
        new_upload.save()

        try:
            file = default_storage.open(new_upload.upload_file.name, 'rb')
        except OSError as oe:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': [oe]}}
            log.error(report['errors'])
            return report
        except Exception as e:
            report['total_errors'] = 1
            report['errors'] = 'Indeterminate error.'
            log.error(e)
            return report

        log.info(f'User: {request.user.username} uploaded file: "{file}" ({new_upload})')

        cuef = None
        report = {
            'file': request.FILES['upload_file']._name,
            'time': new_upload.upload_timestamp,
            'size': os.path.getsize(settings.MEDIA_ROOT + new_upload.upload_file.name) >> 10,
            'upload_id': new_upload.upload_id, }

        try:
            cuef = CofkUploadExcelFile(new_upload, file)

            elapsed = round(time.time() - start)

            if not elapsed:
                elapsed = '1 second'
            else:
                elapsed = f'{elapsed + 1} seconds'

            report['elapsed'] = elapsed

        except CofkExcelFileError as cmce:
            errors = [str(cmce)]
            report['total_errors'] = len(errors)
            report['errors'] = {'file': {'total': len(errors), 'error': errors}}
            log.error(cmce.msg)
        except (FileNotFoundError, BadZipFile, OSError) as e:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': ['Could not read the file.']}}
            log.error(e)
        except ValueError as ve:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': [ve]}}
            log.error(ve)
        except Exception as e:
            report['total_errors'] = 1
            report['errors'] = 'Indeterminate error.'
            log.error(e)

        if cuef and cuef.errors:
            log.error(f'Deleting upload {new_upload}')
            new_upload.delete()
            # TODO delete uploaded file
            report['errors'] = cuef.errors
            report['total_errors'] = cuef.total_errors
        elif 'total_errors' in report:
            log.error(f'Deleting upload {new_upload}')
            new_upload.delete()
        else:
            new_upload.upload_name = request.FILES['upload_file']._name + ' ' + str(new_upload.upload_timestamp)
            new_upload.uploader_email = request.user.email
            new_upload.upload_username = f'{request.user.forename} {request.user.surname}'
            new_upload.save()
    else:
        report['errors'] = 'Form invalid'

    return report


@method_decorator([login_required,
                   permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)],
                  name='dispatch')
class UploadView(ListView):
    model = CofkCollectUpload
    ordering = '-upload_timestamp'
    template_name = 'uploader/list.html'
    paginate_by = 250

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        # Filter so only uploads Awaiting review or Partly reviewed are displayed
        return qs.filter(upload_status_id__in=[1, 2])

    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)

        if kwargs:
            response.context_data |= kwargs

        return response


@method_decorator([login_required,
                   permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)],
                  name='dispatch')
class AddUploadView(TemplateView):
    template_name = "uploader/form.html"
    form = CofkCollectUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form to create new upload
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        report = kwargs['report'] = handle_upload(request)

        # If workbook upload is successful redirect to review view
        if 'total_errors' not in report:
            return redirect(f'/upload/{report["upload_id"]}')

        return self.get(self, request, *args, **kwargs)


@login_required
@permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)
def upload_review(request, upload_id, **kwargs):
    template_url = 'uploader/review.html'
    upload = CofkCollectUpload.objects.filter(upload_id=upload_id).first()

    works_paginator = Paginator(DisplayableCollectWork.objects.filter(upload=upload).order_by('pk'), 99999)
    page_number = request.GET.get('page', 1)
    works_page = works_paginator.get_page(page_number)

    # TODO, are all of these required for context?
    context = {'upload': upload,
               'works_page': works_page,
               'authors': CofkCollectAuthorOfWork.objects.filter(upload=upload),
               'addressees': CofkCollectAddresseeOfWork.objects.filter(upload=upload),
               'mentioned': CofkCollectPersonMentionedInWork.objects.filter(upload=upload),
               'languages': CofkCollectLanguageOfWork.objects.filter(upload=upload),
               'subjects': CofkCollectSubjectOfWork.objects.filter(upload=upload),
               # Authors, addressees and mentioned link to People, here we're only
               # passing new people for review purposes
               'people': CofkCollectPerson.objects.filter(upload=upload, union_iperson__isnull=True),
               'places': CofkCollectLocation.objects.filter(upload=upload, union_location__isnull=True),
               'destinations': CofkCollectDestinationOfWork.objects.filter(upload=upload),
               'origins': CofkCollectOriginOfWork.objects.filter(upload=upload),
               'institutions': CofkCollectInstitution.objects.filter(upload=upload),
               'manifestations': CofkCollectManifestation.objects.filter(upload=upload),
               'resources': CofkCollectWorkResource.objects.filter(upload=upload)}

    if 'accept_all' in request.POST or 'accept_work' in request.POST:
        context['accept_work'] = True
        context['catalogues'] = CofkLookupCatalogue.objects.all()

        work_id = request.POST['work_id'] if 'work_id' in request.POST else None

        if work_id:
            context['work'] = get_work(context['works_page'].paginator.object_list, work_id)[0]
    elif 'confirm_accept' in request.POST:
        accept_works(request, context, upload)
    elif 'reject_all' in request.POST or 'reject_work' in request.POST:
        reject_works(request, context, upload)

    return render(request, template_url, context)


def lookup_fn_date_of_work(lookup_fn, field_name, value):
    value = str(value).strip()
    query = Q()
    date_pattern = r'^([\d\?]{4})(?:-([\d]{2}|[\?]{2}))?(?:-([\d]{2}|[\?]{2}))?$'
    matches = [re.search(date_pattern, v) for v in value.split(' to ')]

    if len(matches) == 1:
        year = matches[0].group(1)
        month = matches[0].group(2)
        day = matches[0].group(3)

        if year and year != '????':
            query &= Q(date_of_work_std_year=year)

        if month and month != '??':
            query &= Q(date_of_work_std_month=month)

        if day and day != '??':
            query &= Q(date_of_work_std_day=day)
    elif len(matches) == 2:
        year = matches[0].group(1)
        month = matches[0].group(2)
        day = matches[0].group(3)
        year2 = matches[1].group(1)
        month2 = matches[1].group(2)
        day2 = matches[1].group(3)

        if year and year != '????':
            query &= Q(date_of_work_std_year__gte=year)

        if month and month != '??':
            query &= Q(date_of_work_std_month__gte=month)

        if day and day != '??':
            query &= Q(date_of_work_std_day__gte=day)

        if year2 and year2 != '????':
            query &= Q(date_of_work_std_year__lte=year2)

        if month2 and month2 != '??':
            query &= Q(date_of_work_std_month__lte=month2)

        if day2 and day2 != '??':
            query &= Q(date_of_work_std_day__lte=day2)

    else:
        query = Q(pk=0)

    return query



def lookup_fn_issues(value):

    cond_map = [
        (r'Date\s+of\s+work\s+INFERRED', lambda: Q(date_of_work_inferred=1)),
        (r'Date\s+of\s+work\s+UNCERTAIN', lambda: Q(date_of_work_uncertain=1)),
        (r'Date\s+of\s+work\s+APPROXIMATE', lambda: Q(date_of_work_approx=1)),
        (r'Author\s*/\s*sender\s+INFERRED', lambda: Q(authors_inferred=1)),
        (r'Author\s*/\s*sender\s+UNCERTAIN', lambda: Q(authors_uncertain=1)),
        (r'Addressee\s+INFERRED', lambda: Q(addressees_inferred=1)),
        (r'Addressee\s+UNCERTAIN', lambda: Q(addressees_uncertain=1)),
        (r'Origin\s+INFERRED', lambda: Q(origin_inferred=1)),
        (r'Origin\s+UNCERTAIN', lambda: Q(origin_uncertain=1)),
        (r'Destination\s+INFERRED', lambda: Q(destination_inferred=1)),
        (r'Destination\s+UNCERTAIN', lambda: Q(destination_uncertain=1)),
        (r'People\s+mentioned\s+INFERRED', lambda: Q(mentioned_inferred=1)),
        (r'People\s+mentioned\s+UNCERTAIN', lambda: Q(mentioned_uncertain=1)),
        (r'Place\s+mentioned\s+INFERRED', lambda: Q(place_mentioned_inferred=1)),
        (r'Place\s+mentioned\s+UNCERTAIN', lambda: Q(place_mentioned_uncertain=1)),
    ]

    query = Q()
    for pattern, q in cond_map:
        if re.search(pattern, value, re.IGNORECASE):
            query |= q()
    return query

class ColWorkSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data)]

    @property
    def search_field_label_map(self) -> dict:
        return field_label_map['collect_work']

    @property
    def search_field_fn_maps(self) -> dict[str, Lookup]:
        return create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                   'change_timestamp')

    @property
    def entity(self) -> str:
        return 'uploaded work,uploaded works'

    @property
    def default_order(self) -> str:
        return 'asc'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('union_iwork_id', 'ID in main database',),
            ('source', 'Source',),
            ('contact', 'Contact',),
            ('status', 'Status of work'),
            ('editors_notes', 'Editors\'s notes',),
            ('date_of_work_sort', 'Date of work'),
            ('date_of_work_as_marked', 'Date of work as marked'),
            ('original_calendar', 'Original calendar'),
            ('notes_on_date_of_work', 'Notes on date of work'),
            ('authors', 'Authors'),
            ('authors_as_marked', 'Authors as marked'),
            ('notes_on_authors', 'Notes on authors'),
            ('origin', 'Origin'),
            ('origin_as_marked', 'Origin as marked'),
            ('addressees', 'Addressees'),
            ('addressees_as_marked', 'Addressees as marked'),
            ('notes_on_addressees', 'Notes on addressees'),
            ('destination', 'Destination'),
            ('destination_as_marked', 'Destination as marked'),
            ('manifestations', 'Manifestations'),
            ('abstract', 'Abstract'),
            ('keywords', 'Keywords'),
            ('languages', 'Languages of work'),
            ('subjects', 'Subjects of work'),
            ('incipit', 'Incipit'),
            ('excipit', 'Excipit'),
            ('people_mentioned', 'People mentioned'),
            ('notes_on_people_mentioned', 'Notes on people mentioned'),
            ('places_mentioned', 'Places mentioned'),
            # ('issues', 'Issues'),
            ('notes_on_letter', 'Notes on letter'),
            ('resources', 'Related resources'),
            ('upload_id', 'Upload ID'),
            ('iwork_id', 'Work ID in tool'),
        ]

    @property
    def search_field_combines(self) -> dict[str: list[str]]:
        return {'source': ['accession_code'],
                'contact': ['upload__uploader_email'],
                'status': ['upload_status__status_desc'],
                'id_main': ['union_iwork__pk'],
                'authors': ['authors__iperson__primary_name'],
                'addressees': ['addressees__iperson__primary_name'],
                'origin': ['origin__location__location_name'],
                'destination': ['destination__location__location_name'],
                'manifestations': ['manifestations__repository__institution_name',
                                   'manifestations__id_number_or_shelfmark',
                                   'manifestations__printed_edition_details',
                                   'manifestations__manifestation_notes'],
                'languages': ['languages__language_code__language_name'],
                'subjects': ['subjects__subject__subject_desc'],
                'people_mentioned': ['people_mentioned__iperson__primary_name'],
                'places_mentioned': ['places_mentioned__location__location_name'],
                'resources': ['resources__resource_name', 'resources__resource_url'],
                'upload_id': ['upload__pk'],
                'date_of_work_sort': ['date_of_work_std_year', 'date_of_work_std_month',
                                      'date_of_work_std_day']}

    def get_queryset(self):
        if not self.request_data:
            return DisplayableCollectWork.objects.none()

        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        # queries for like_fields
        queries = create_queries_by_field_fn_maps(request_data, self.search_field_fn_maps)

        queries.extend(
            create_queries_by_lookup_field(request_data,
                                           search_field_names=self.search_fields,
                                           search_fields_maps=self.search_field_combines,
                                           search_fields_fn_maps={'issues': lookup_fn_issues,
                                                                  'date_of_work': lookup_fn_date_of_work})
        )

        return self.create_queryset_by_queries(DisplayableCollectWork, queries, sort_by=sort_by)

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return create_table_search_results_renderer('uploader/search_table_layout.html')
