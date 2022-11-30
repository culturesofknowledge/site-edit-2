import itertools
import logging
import os
from abc import ABC
from multiprocessing import Process
from typing import Iterable, Type, Callable
from typing import NoReturn
from typing import Optional
from urllib.parse import urlencode

from django import template
from django.conf import settings
from django.db import models
from django.forms import ModelForm, BaseForm, BaseFormSet
from django.forms import formset_factory
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

import core.constant as core_constant
from core.forms import ImageForm, UploadImageForm, ResourceForm
from core.forms import RecrefForm
from core.forms import build_search_components
from core.helper import file_utils, email_utils, recref_utils, iter_utils
from core.helper import model_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.renderer_utils import CompactSearchResultsRenderer, DemoCompactSearchResultsRenderer, \
    demo_table_search_results_renderer
from core.helper.view_components import DownloadCsvHandler
from core.models import Recref
from core.services import media_service
from uploader.models import CofkUnionImage, CofkUnionSubject, CofkUnionRoleCategory

register = template.Library()
log = logging.getLogger(__name__)


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    paginate_by = 100
    template_name = 'core/basic_search_page.html'
    context_object_name = 'records'

    @property
    def query_fieldset_list(self) -> Iterable:
        """
        return iterable form that can render search fieldset for searching
        """
        raise NotImplementedError()

    @property
    def entity(self) -> str:
        """
        return str containing singular and plural for entity separated by a comma
        """
        raise NotImplementedError()

    def expanded_query_fieldset_list(self) -> Iterable:
        """
        return iterable form for expanded view that can render search fieldset for searching
        """
        return self.query_fieldset_list

    @property
    def title(self) -> str:
        raise NotImplementedError()

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        """
        return list of tuple for "django field value" and "Label"
        Example :
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
            ('-location_name', 'Location Name desc',),
            ('location_name', 'Location Name asc',),
        ]

        """
        raise NotImplementedError()

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        """ factory of Compact layout """
        raise NotImplementedError('missing compact_search_results_renderer_factory')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        """ factory of Table layout """
        raise NotImplementedError('missing table_search_results_renderer_factory')

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        raise NotImplementedError('missing download_csv_handler')

    @property
    def merge_page_vname(self) -> str:
        # KTODO merge feature can be disable
        raise NotImplementedError('missing merge_page_vname')

    @property
    def return_quick_init_vname(self) -> str:
        # KTODO return_quick_init feature can be disable
        raise NotImplementedError('missing return_quick_init_vname')

    def get_queryset(self):
        raise NotImplementedError('missing get_queryset')

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_sort_by(self):
        if self.request_data.get('order') == 'asc':
            return self.request_data.get('sort_by', self.sort_by_choices[0][0])

        return '-' + self.request_data.get('sort_by', self.sort_by_choices[0][0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recref_mode'] = self.request_data.get('recref_mode', '0')

        search_components_factory = build_search_components(self.sort_by_choices)

        default_search_components_dict = {
            'num_record': str(self.paginate_by),
            'sort_by': self.get_sort_by(),
        }
        is_compact_layout = (self.request_data.get('display-style', core_constant.SEARCH_LAYOUT_TABLE)
                             == core_constant.SEARCH_LAYOUT_GRID)
        results_renderer = (self.compact_search_results_renderer_factory
                            if is_compact_layout
                            else self.table_search_results_renderer_factory)

        query_fieldset_list = self.query_fieldset_list if is_compact_layout else self.expanded_query_fieldset_list

        context.update({'query_fieldset_list': query_fieldset_list,
                        'search_components': search_components_factory(default_search_components_dict |
                                                                       self.request_data.dict()),
                        'total_record': self.get_queryset().count(),
                        'entity': self.entity or '',
                        'title': self.entity.split(',')[1].title() if self.entity else 'Title',
                        'results_renderer': results_renderer(context[self.context_object_name]),
                        'is_compact_layout': is_compact_layout,
                        'to_user_messages': getattr(self, 'to_user_messages', []),
                        'merge_page_url': reverse(self.merge_page_vname),
                        'return_quick_init_vname': self.return_quick_init_vname,
                        })

        return context

    @staticmethod
    def send_csv_email(csv_handler, queryset, to_email):
        csv_path = file_utils.create_new_tmp_file_path()
        csv_handler.create_csv_file(csv_path, queryset)

        if not to_email:
            log.error(f'unknown user email -- [{to_email}]')

        resp = email_utils.send_email(
            to_email,
            subject='Search result',
            attachments=[
                ('search_result.csv', open(csv_path, mode='rb'), 'text/csv')
            ],
        )
        log.info(f'csv file email have be send to [{to_email}]')
        os.remove(csv_path)
        log.debug('email resp', resp)

    def resp_download_csv(self, request, *args, **kwargs):

        def _fn():
            try:
                self.send_csv_email(self.download_csv_handler, self.get_queryset(), request.user.email)
            except Exception as e:
                log.error('send csv email fail....')
                log.exception(e)

        # create csv file and send email in other process
        Process(target=_fn).start()

        # stay as same page
        self.to_user_messages = ['Csv file will be send to your email later.']
        return super().get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        simple_form_action_map = {
            'download_csv': self.resp_download_csv,
        }

        # simple routing with __form_action
        if resp_fn := simple_form_action_map.get(self.request_data.get("__form_action")):
            return resp_fn(request, *args, **kwargs)

        if num_record := request.GET.get('num_record'):
            self.paginate_by = num_record

        # response for search query
        return super().get(request, *args, **kwargs)


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        return '?{}'.format(urlencode(safe_args))
    return ''


class DefaultSearchView(BasicSearchView):

    @property
    def query_fieldset_list(self) -> Iterable:
        return []

    @property
    def entity(self) -> str:
        return '__ENTITIES__,__ENTITY__'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return DemoCompactSearchResultsRenderer

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return demo_table_search_results_renderer

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        return None

    @property
    def merge_page_vname(self) -> str:
        return 'login:gate'

    @property
    def return_quick_init_vname(self) -> str:
        return 'login:gate'

    def get_queryset(self):
        class _FakeQueryset(list):

            def count(self, *args, **kwargs):
                return 0

        return _FakeQueryset()


class CommonInitFormViewTemplate(View):

    def resp_form_page(self, request, form):
        raise NotImplementedError()

    def resp_after_saved(self, request, form, new_instance):
        raise NotImplementedError()

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        raise NotImplementedError()

    def on_form_changed(self, request, form) -> NoReturn:
        if hasattr(form.instance, 'update_current_user_timestamp'):
            form.instance.update_current_user_timestamp(request.user.username)
        _new_instance = form.save()
        log.info(f'records saved [{_new_instance}]')
        return _new_instance

    def post(self, request, *args, **kwargs):
        form = self.form_factory(request.POST or None)
        if form.is_valid():
            log.info(f'form have been changed')
            new_instance = self.on_form_changed(request, form)
            return self.resp_after_saved(request, form, new_instance)

        return self.resp_form_page(request, form)

    def get(self, request, *args, **kwargs):
        form = self.form_factory()
        return self.resp_form_page(request, form)


def render_return_quick_init(request, name, item_name, item_id):
    return render(request, 'core/return_quick_init.html', {
        'name': name,
        'item_name': item_name,
        'item_id': item_id,
    })


def any_invalid_with_log(form_formsets: Iterable):
    for f in form_formsets:
        if not f.is_valid():
            log.debug(f'form is invalid [{type(f)}] '
                      f'-- [{getattr(f, "error_messages", None)}] '
                      f'-- [{repr(getattr(f, "errors", None))}]')
            return True

    return False


def create_formset(form_class, post_data=None, prefix=None,
                   initial_list: Iterable[dict] = None,
                   extra=1):
    initial_list = initial_list or []
    initial_list = list(initial_list)
    return formset_factory(form_class, extra=extra)(
        post_data or None,
        prefix=prefix,
        initial=initial_list,
    )


class MultiRecrefHandler:
    """
    provide common workflow handle multi recref records
    * create, delete , update record
    * create form and formset
    """

    def __init__(self, request_data, name,
                 recref_form_class: Type[RecrefForm] = RecrefForm,
                 initial_list=None):

        self.name = name
        self.new_form = recref_form_class(request_data or None, prefix=f'new_{name}')
        self.update_formset = create_formset(recref_form_class, post_data=request_data,
                                             prefix=f'recref_{name}',
                                             initial_list=initial_list,
                                             extra=0, )

    def create_context(self) -> dict:
        return {
            f'recref_{self.name}': {
                'new_form': self.new_form,
                'update_formset': self.update_formset,
            },
        }

    @property
    def recref_class(self) -> Type[models.Model]:
        raise NotImplementedError()

    def create_recref_by_new_form(self, target_id, parent_instance) -> Optional[Recref]:
        raise NotImplementedError()

    def maintain_record(self, request, parent_instance):
        """
        workflow for handle:
        create, update, delete recref record by form data
        """
        # save new_form
        self.new_form.is_valid()
        if target_id := self.new_form.cleaned_data.get('target_id'):
            if recref := self.create_recref_by_new_form(target_id, parent_instance):
                recref = recref_utils.fill_common_recref_field(recref, self.new_form.cleaned_data,
                                                               request.user.username)
                recref.save()
                log.info(f'create new recref [{recref}]')

        # update update_formset
        target_changed_fields = {'to_date', 'from_date', 'is_delete'}
        _forms = (f for f in self.update_formset if not target_changed_fields.isdisjoint(f.changed_data))
        for f in _forms:
            f.is_valid()
            recref_id = f.cleaned_data['recref_id']
            if f.cleaned_data['is_delete']:
                log.info(f'remove recref [{recref_id=}]')
                self.recref_class.objects.filter(pk=recref_id).delete()
            else:
                log.info(f'update recref [{recref_id=}]')
                ps_loc = self.recref_class.objects.get(pk=recref_id)
                ps_loc = recref_utils.fill_common_recref_field(ps_loc, f.cleaned_data, request.user.username)
                ps_loc.save()


class MultiRecrefAdapterHandler(MultiRecrefHandler):
    def __init__(self, request_data, name,
                 recref_adapter: RecrefFormAdapter,
                 recref_form_class,
                 rel_type='is_reply_to',
                 ):
        self.recref_adapter = recref_adapter
        self.rel_type = rel_type
        initial_list = (m.__dict__ for m in self.recref_adapter.find_recref_records(self.rel_type))
        initial_list = (recref_utils.convert_to_recref_form_dict(r, self.recref_adapter.target_id_name(),
                                                                 self.recref_adapter.find_target_display_name_by_id)
                        for r in initial_list)
        super().__init__(request_data, name=name, initial_list=initial_list,
                         recref_form_class=recref_form_class)

    @property
    def recref_class(self) -> Type[Recref]:
        return self.recref_adapter.recref_class()

    def create_recref_by_new_form(self, target_id, parent_instance) -> Optional[Recref]:
        return recref_utils.upsert_recref_by_target_id(
            target_id, self.recref_adapter.find_target_instance,
            rel_type=self.rel_type,
            parent_instance=parent_instance,
            create_recref_fn=self.recref_class,
            set_parent_target_instance_fn=self.recref_adapter.set_parent_target_instance,
        )


class FullFormHandler:
    """ maintain collections of Form and Formset for View
    developer can define instance of Form and Formset in `load_data`

    this class provide many tools for View
    like `all_named_form_formset`, `save_all_comment_formset`
    """

    def __init__(self, pk, *args, request_data=None, request=None, **kwargs):
        self.recref_formset_handlers: list[RecrefFormsetHandler] = []
        self.load_data(pk,
                       request_data=request_data or None,
                       request=request, *args, **kwargs)

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        raise NotImplementedError()

    def all_img_recref_handlers(self) -> Iterable[tuple[str, 'ImageRecrefHandler']]:
        return ((name, var) for name, var in self.__dict__.items()
                if isinstance(var, ImageRecrefHandler))

    def find_all_named_form_formset(self) -> Iterable[tuple[str, BaseForm | BaseFormSet]]:
        """
        find all variables in full_form_handler that is BaseForm or BaseFormSet
        """
        attr_list = ((name, var) for name, var in self.__dict__.items()
                     if isinstance(var, (BaseForm, BaseFormSet)))
        return attr_list

    @property
    def every_form_formset(self):
        return itertools.chain(
            (ff for _, ff in self.find_all_named_form_formset()),
            itertools.chain.from_iterable(
                (h.new_form, h.update_formset) for h in self.all_recref_handlers
            ),
            itertools.chain.from_iterable(
                (h.upload_img_form, h.formset) for _, h in self.all_img_recref_handlers()
            ),
            (h.formset for h in self.recref_formset_handlers),
        )

    def is_any_changed(self):
        for f in self.every_form_formset:
            if f.has_changed():
                if isinstance(f, BaseFormSet):
                    changed_data = set(itertools.chain.from_iterable(
                        _f.changed_data for _f in f.forms
                    ))
                else:
                    changed_data = f.changed_data
                log.debug(f'form or formset changed [{f.__class__.__name__}][{changed_data}]')
                return True

        return False

    def maintain_all_recref_records(self, request, parent_instance):
        for recref_handler in self.all_recref_handlers:
            recref_handler.maintain_record(request, parent_instance)

    @property
    def all_recref_handlers(self):
        attr_list = (getattr(self, p) for p in dir(self))
        attr_list = (a for a in attr_list if isinstance(a, MultiRecrefHandler))
        return attr_list

    def add_recref_formset_handler(self, recref_formset_handler: 'RecrefFormsetHandler'):
        self.recref_formset_handlers.append(recref_formset_handler)

    def save_all_recref_formset(self, parent, request):
        # KTODO fix comment_id has_changed problem
        for c in self.recref_formset_handlers:
            c.save(parent, request)

    def create_context(self):
        context = dict(self.find_all_named_form_formset())
        for _, img_handler in self.all_img_recref_handlers():
            context.update(img_handler.create_context())
        for h in self.all_recref_handlers:
            context.update(h.create_context())
        context.update({h.context_name: h.formset
                        for h in self.recref_formset_handlers})

        return context

    def is_invalid(self):
        form_formsets = (f for f in self.every_form_formset if f.has_changed())
        return any_invalid_with_log(form_formsets)

    def prepare_cleaned_data(self):
        for f in self.every_form_formset:
            f.is_valid()


class RecrefFormsetHandler:
    """
    Handle form for *target* instance.
    * help for create formset
    * help for save target instance and create recref records
    """

    def __init__(self, prefix, request_data,
                 form: Type[ModelForm],
                 rel_type,
                 parent: models.Model,
                 context_name=None,
                 ):
        recref_adapter = self.create_recref_adapter(parent)
        self.context_name = context_name or f'{prefix}_formset'
        self.rel_type = rel_type
        self.formset = create_formset(
            form, post_data=request_data,
            prefix=prefix,
            initial_list=model_utils.models_to_dict_list(
                recref_adapter.find_all_targets_by_rel_type(rel_type)
            )
        )

    def create_context(self):
        return {
            self.context_name: self.formset,
        }

    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        raise NotImplementedError()

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        raise NotImplementedError()

    def save(self, parent, request):
        self.save_form_list(
            parent, request,
            (f for f in self.formset if f.has_changed()),
        )

    @staticmethod
    def _save_formset(forms: Iterable[ModelForm],
                      model_id_name=None,
                      form_id_name=None,
                      username=None, ):
        _forms = (f for f in forms if f.has_changed())
        for form in _forms:
            log.debug(f'form has changed : {form.changed_data}')

            form.is_valid()  # make sure cleaned_data exist
            form_id_name = form_id_name or model_id_name
            form_target_id = form.cleaned_data.get(form_id_name)

            if form_target_id is None:
                # create
                if username and hasattr(form.instance, 'update_current_user_timestamp'):
                    form.instance.update_current_user_timestamp(username)
                form.save()
                log.info(f'recref_formset created -- [{form.instance}]')

            else:
                # update
                db_model: models.Model = form.instance._meta.model.objects.get(**{model_id_name: form_target_id})

                for field in form.changed_data:
                    if hasattr(db_model, field):
                        setattr(db_model, field, form.cleaned_data[field])

                if username and hasattr(db_model, 'update_current_user_timestamp'):
                    db_model.update_current_user_timestamp(username)

                db_model.save()
                form.instance = db_model
                log.info(f'recref_formset updated -- [{db_model}]')

    def save_form_list(self, parent, request, forms: Iterable[ModelForm]):
        recref_adapter: RecrefFormAdapter = self.create_recref_adapter(parent)
        forms = list(forms)

        # save each target instance
        self._save_formset(forms, model_id_name=recref_adapter.target_id_name(),
                           username=request.user.username)

        # upsert each recref
        for target in (f.instance for f in forms):
            org_recref = self.find_org_recref_fn(
                parent=parent,
                target=target,
            )

            recref = recref_adapter.upsert_recref(self.rel_type, parent,
                                                  target,
                                                  username=request.user.username,
                                                  org_recref=org_recref,
                                                  )
            recref.save()
            log.info(f'save m2m recref -- [{recref}][{target}]')


class TargetResourceFormsetHandler(RecrefFormsetHandler, ABC):

    def __init__(self, request_data, parent: models.Model,
                 rel_type=core_constant.REL_TYPE_IS_RELATED_TO,
                 prefix='res',
                 form: Type[ModelForm] = ResourceForm,
                 context_name=None):
        super().__init__(prefix, request_data, form, rel_type, parent, context_name)

    def save(self, parent, request):
        del_forms, saved_forms = iter_utils.split(
            (f for f in self.formset if f.has_changed()),
            lambda f: f.cleaned_data['is_delete'],
        )

        # handle del
        recref_adapter: RecrefFormAdapter = self.create_recref_adapter(parent)
        for form in del_forms:
            target_id_name = recref_adapter.target_id_name()
            if form_target_id := form.cleaned_data.get(target_id_name):
                form.instance._meta.model.objects.filter(**{target_id_name: form_target_id}).delete()
                log.info(f'del resources recref [{form_target_id}][{form.cleaned_data}]')
            else:
                log.warning(f'skip del, form target id not found [{target_id_name}][{form_target_id}]')

        # handle save / update
        super().save_form_list(parent, request, forms=saved_forms)


class ImageRecrefHandler(RecrefFormsetHandler, ABC):
    def __init__(self, request_data, request_files, parent: models.Model,
                 rel_type=core_constant.REL_TYPE_IMAGE_OF,
                 prefix='image', context_name=None):
        super().__init__(prefix, request_data, ImageForm, rel_type, parent, context_name)
        self.parent = parent
        self.upload_img_form = UploadImageForm(request_data or None, request_files)

    def create_context(self):
        total_images = len(list(self.create_recref_adapter(self.parent).find_recref_records(self.rel_type)))
        return {
            'img_handler': {
                'image_formset': self.formset,
                'img_form': self.upload_img_form,
                'total_images': total_images,
            }
        }

    def save(self, parent, request):
        super().save(parent, request)

        # save if user uploaded an image
        self.upload_img_form.is_valid()
        if uploaded_img_file := self.upload_img_form.cleaned_data.get('selected_image'):
            file_path = media_service.save_uploaded_img(uploaded_img_file)
            file_url = media_service.get_img_url_by_file_path(file_path)
            img_obj = CofkUnionImage(image_filename=file_url, display_order=0,
                                     licence_details='', credits='',
                                     licence_url=settings.DEFAULT_IMG_LICENCE_URL)
            img_obj.update_current_user_timestamp(request.user.username)
            img_obj.save()

            # create recref records
            recref_adapter = self.create_recref_adapter(parent)
            recref = recref_adapter.upsert_recref(self.rel_type, parent, img_obj,
                                                  username=request.user.username)
            recref.save()


class RecrefCheckbox:
    def __init__(self, target_id, desc, is_selected, name):
        self.target_id = target_id
        self.desc = desc
        self.is_selected = is_selected
        self.name = name

    def __call__(self, *args, **kwargs):
        context = {
            'target_id': self.target_id,
            'desc': self.desc,
            'is_selected': self.is_selected,
            'name': self.name,
        }
        return render_to_string('core/component/recref_checkbox.html', context)


class RecrefCheckboxHandler:

    def __init__(self, recref_adapter: RecrefFormAdapter, rel_type: str, name: str,
                 target_class: Type[models.Model],
                 ):
        self.recref_adapter = recref_adapter
        self.rel_type = rel_type
        self.name = name
        self.target_class = target_class

    def get_target_id_label(self, target):
        raise NotImplementedError()

    def _create_ui_data(self, target: models.Model, selected_id_list):
        target_id, label = self.get_target_id_label(target)
        return RecrefCheckbox(
            target_id=target_id,
            desc=label,
            is_selected=target_id in selected_id_list,
            name=self.name,
        )

    def create_context(self):
        selected_id_list = set(self.recref_adapter.find_targets_id_list(self.rel_type))
        return {
            self.name: (self._create_ui_data(s, selected_id_list) for s in self.target_class.objects.all()),
        }

    def get_selected_target_id_list(self, request):
        return request.POST.getlist(self.name)

    def find_changed_list(self, request):
        org_recref_list = list(self.recref_adapter.find_recref_records(self.rel_type))
        org_id_list = {self.recref_adapter.get_target_id(r) for r in org_recref_list}

        selected_id_list = {int(s) for s in self.get_selected_target_id_list(request)}
        del_recref_list = [recref for recref in org_recref_list
                           if self.recref_adapter.get_target_id(recref) not in selected_id_list]
        new_id_set = selected_id_list - org_id_list
        return new_id_set, del_recref_list

    def has_changed(self, request):
        new_id_set, del_recref_list = self.find_changed_list(request)
        return new_id_set or del_recref_list

    def save(self, request, parent):
        self.recref_adapter.parent = parent

        new_id_set, del_recref_list = self.find_changed_list(request)

        # delete
        for recref in del_recref_list:
            log.info(f'remove {self.name} recref [{parent}][{recref.pk}]')
            recref.delete()

        # add
        for new_target_id in new_id_set:
            log.info(f'add {self.name} recref [{parent}][{new_target_id}]')
            if not (target := self.recref_adapter.find_target_instance(new_target_id)):
                raise ValueError(f'not found [{new_target_id}]')

            recref = self.recref_adapter.upsert_recref(self.rel_type, parent, target,
                                                       username=request.user.username)
            recref.save()


class SubjectHandler(RecrefCheckboxHandler):

    def __init__(self, recref_adapter: RecrefFormAdapter,
                 rel_type: str = core_constant.REL_TYPE_DEALS_WITH,
                 name: str = 'subjects', ):
        super().__init__(recref_adapter, rel_type, name, CofkUnionSubject)

    def get_target_id_label(self, target):
        target: CofkUnionSubject
        return target.subject_id, target.subject_desc


class RoleCategoryHandler(RecrefCheckboxHandler):
    def __init__(self, recref_adapter: RecrefFormAdapter,
                 rel_type: str = core_constant.REL_TYPE_MEMBER_OF,
                 name: str = 'roles', ):
        super().__init__(recref_adapter, rel_type, name, CofkUnionRoleCategory)

    def get_target_id_label(self, target):
        target: CofkUnionRoleCategory
        return target.role_category_id, target.role_category_desc
