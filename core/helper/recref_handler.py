"""
recref_handler tools for help load and update recref record in `view`

as you can see in form, website have multi ways to create recref records
such as:
* only one relation (SingleRecrefHandler)
* multi relations (MultiRecrefHandler)
* multi relations by checkbox (RecrefCheckbox)
* multi relation and create new instance (RecrefFormsetHandler)
"""

import logging
from abc import ABC
from typing import Type, Iterable, Optional

from django.conf import settings
from django.db import models
from django.forms import forms, ModelForm
from django.template.loader import render_to_string

from core import constant as core_constant
from core.forms import ImageForm, UploadImageForm, ResourceForm, RecrefForm
from core.helper import recref_utils, model_utils, iter_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.view_utils import create_formset
from core.models import Recref
from core.services import media_service
from uploader.models import CofkUnionSubject, CofkUnionRoleCategory, CofkUnionImage

log = logging.getLogger(__name__)


class SingleRecrefHandler:
    """
    some recref only allow select one target in frontend
    this class help you to load(init) and save for single recref situation
    """

    def __init__(self, form_field_name, rel_type, create_recref_adapter_fn):
        self.form_field_name = form_field_name
        self.rel_type = rel_type
        self.create_recref_adapter = create_recref_adapter_fn

    def create_init_dict(self, parent: models.Model):
        if parent is None:
            return dict()

        recref_adapter = self.create_recref_adapter(parent)
        recref = self._find_recref_by_parent(parent, recref_adapter=recref_adapter)
        return {
            self.form_field_name: recref_adapter.get_target_id(recref),
        }

    def _find_recref_by_parent(self, parent, recref_adapter=None):
        recref_adapter = recref_adapter or self.create_recref_adapter(parent)
        recref = next(recref_adapter.find_recref_records(self.rel_type), None)
        return recref

    def upsert_recref_if_field_exist(self, form: forms.BaseForm, parent, username,
                                     ):
        if not (target_id := form.cleaned_data.get(self.form_field_name)):
            log.debug(f'value of form_field_name not found [{self.form_field_name=}] ')
            return

        recref_adapter = self.create_recref_adapter(parent)
        recref_adapter.target_id_name()
        recref = recref_utils.upsert_recref_by_target_id(
            target_id, recref_adapter.find_target_instance,
            rel_type=self.rel_type,
            parent_instance=parent,
            create_recref_fn=recref_adapter.recref_class(),
            set_parent_target_instance_fn=recref_adapter.set_parent_target_instance,
            org_recref=self._find_recref_by_parent(parent, recref_adapter),
            username=username,
        )
        recref.save()
        return recref


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
