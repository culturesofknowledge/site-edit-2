import logging
import os
import re
from typing import Iterable

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Lookup
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from django_q.tasks import AsyncTask

from core import constant
from core.form_label_maps import field_label_map
from core.helper.query_serv import create_from_to_datetime, create_queries_by_field_fn_maps, \
    create_queries_by_lookup_field
from core.helper.renderer_serv import create_table_search_results_renderer, RendererFactory
from core.helper.uploader_serv import handle_upload
from core.helper.view_serv import DefaultSearchView
from core.models import CofkLookupCatalogue, CofkLookupDocumentType
from uploader.forms import CofkCollectUploadForm, GeneralSearchFieldset
from uploader.models import CofkCollectUpload, CofkCollectPerson, CofkCollectLocation
from uploader.review import reject_works
from uploader.uploader_serv import DisplayableCollectWork

log = logging.getLogger(__name__)


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
        return qs.filter(upload_status_id__in=[1, 2]).select_related('upload_status')

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
        form = CofkCollectUploadForm(request.POST, request.FILES)
        report = {}

        if form.is_valid() and 'upload_file' in request.FILES:
            filename = request.FILES['upload_file'].name
            upload = form.save(commit=False)
            upload.upload_status_id = 1
            upload.upload_username = f'{request.user.forename} {request.user.surname}'
            upload.uploader_email = request.user.email
            upload.upload_timestamp = timezone.now()
            upload.upload_name = filename + ' ' + str(upload.upload_timestamp)
            upload.save()

            size = os.path.getsize(settings.MEDIA_ROOT + upload.upload_file.name) >> 10

            if size > settings.UPLOAD_ASYNCHRONOUS_FILESIZE_LIMIT:
                task = AsyncTask('core.helper.uploader_serv.handle_upload', upload, True, filename)
                task.run()

                kwargs['report'] = {'async': True,
                                    'file': filename,
                                    'time': upload.upload_timestamp,
                                    'size': size
                                    }
            else:
                report = kwargs['report'] = handle_upload(upload)

                # If workbook upload is successful redirect to review view
                if 'total_errors' not in report:
                    return redirect(reverse('uploader:upload_review', args=[report["upload_id"]]))

        else:
            report['errors'] = 'Form invalid'

        return self.get(self, request, *args, **kwargs)


@login_required
@permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)
def upload_review(request, upload_id, **kwargs):
    template_url = 'uploader/review.html'
    upload: CofkCollectUpload = CofkCollectUpload.objects.filter(pk=upload_id).first()

    prefetch = ['authors', 'addressees', 'people_mentioned', 'languages', 'subjects', 'manifestations', 'resources',
                'upload_status', 'addressees__iperson', 'authors__iperson', 'people_mentioned__iperson',
                'manifestations__repository', 'authors__iperson__union_iperson', 'addressees__iperson__union_iperson',
                'origin__location', 'destination__location', 'origin__location__union_location',
                'destination__location__union_location', 'languages__language_code']

    per_page = request.GET.get('per_page', 1000)

    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 1000

    works_paginator = Paginator(DisplayableCollectWork.objects.filter(upload=upload)
                                .prefetch_related(*prefetch).order_by('pk'), per_page)
    page_number = request.GET.get('page', 1)
    works_page = works_paginator.get_page(page_number)

    doc_types = CofkLookupDocumentType.objects.values_list('document_type_code', 'document_type_desc')
    catalogues = CofkLookupCatalogue.objects.all()
    people = CofkCollectPerson.objects.filter(upload=upload, union_iperson__isnull=True)
    places = CofkCollectLocation.objects.filter(upload=upload, union_location__isnull=True)

    # TODO, are all of these required for context?
    context = {'username': request.user.username,
               'upload': upload,
               'works_page': works_page,
               'people': people,
               'places': places,
               'doc_types': list(doc_types),
               'catalogues': list(catalogues),
               'per_page': per_page,
               'per_page_options': [1000, 2500, 5000]
               }

    # copy variables onto context because we can't pickle the request object which means
    # it can't be passed to Django Q2
    for prop in ['work_id', 'accession_code', 'catalogue_code']:
        if prop in request.POST:
            context[prop] = request.POST[prop]

    if 'confirm' in request.POST and 'action' in request.POST:
        if request.POST['action'] == 'accept':
            task = AsyncTask('uploader.review.accept_works', context, upload,
                             email_addresses=request.user.email)
            task.run()

            msg = (f'The upload {upload.upload_name} is being processed. '
                   f'You will be notified of the results by email sent to {request.user.email}.')
            messages.info(request, msg)

            return redirect(reverse('uploader:upload_list'))
        elif request.POST['action'] == 'reject':
            reject_works(context, upload, request)

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

        queryset = self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

        prefetch = ['upload', 'upload_status', 'work', 'authors', 'authors__iperson',
                    'authors__iperson__union_iperson', 'addressees', 'people_mentioned', 'languages', 'subjects',
                    'manifestations', 'resources', 'addressees__iperson', 'people_mentioned__iperson',
                    'manifestations__repository', 'addressees__iperson__union_iperson',
                    'origin__location', 'destination__location', 'origin__location__union_location',
                    'destination__location__union_location', 'languages__language_code', 'places_mentioned__location',
                    'places_mentioned__location__union_location', 'people_mentioned__iperson',
                    'people_mentioned__iperson__union_iperson']

        return queryset.prefetch_related(*prefetch)

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
