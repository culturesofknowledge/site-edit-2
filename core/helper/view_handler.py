import itertools
import logging
from typing import Iterable

from django.forms import BaseForm, BaseFormSet

from core.helper.recref_handler import ImageRecrefHandler, RecrefFormsetHandler, MultiRecrefHandler
from core.helper.view_serv import any_invalid_with_log

log = logging.getLogger(__name__)


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
        """
        subclass define all form and formset in this method
        or other data that view need
        """
        raise NotImplementedError()

    def all_named_form_formset(self) -> Iterable[tuple[str, BaseForm | BaseFormSet]]:
        """
        find all variables in full_form_handler that is BaseForm or BaseFormSet
        """
        attr_list = ((name, var) for name, var in self.__dict__.items()
                     if isinstance(var, (BaseForm, BaseFormSet)))
        return attr_list

    @property
    def all_recref_handlers(self) -> Iterable[MultiRecrefHandler]:
        attr_list = (getattr(self, p) for p in dir(self))
        attr_list = (a for a in attr_list if isinstance(a, MultiRecrefHandler))
        return attr_list

    def all_img_recref_handlers(self) -> Iterable[tuple[str, 'ImageRecrefHandler']]:
        return ((name, var) for name, var in self.__dict__.items()
                if isinstance(var, ImageRecrefHandler))

    def all_recref_formset_handlers(self) -> Iterable[RecrefFormsetHandler]:
        return self.recref_formset_handlers

    @property
    def every_form_formset(self) -> Iterable[BaseForm | BaseFormSet]:
        return itertools.chain(
            (ff for _, ff in self.all_named_form_formset()),
            itertools.chain.from_iterable(
                (h.new_form, h.update_formset) for h in self.all_recref_handlers
            ),
            itertools.chain.from_iterable(
                (h.upload_img_form, h.formset) for _, h in self.all_img_recref_handlers()
            ),
            (h.formset for h in self.all_recref_formset_handlers()),
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

    def add_recref_formset_handler(self, recref_formset_handler: 'RecrefFormsetHandler'):
        self.recref_formset_handlers.append(recref_formset_handler)

    def save_all_recref_formset(self, parent, request):
        for c in self.all_recref_formset_handlers():
            c.save(parent, request)

    def create_context(self):
        context = dict(self.all_named_form_formset())
        context_list = itertools.chain(
            (h.create_context() for _, h in self.all_img_recref_handlers()),
            (h.create_context() for h in self.all_recref_handlers),
            (h.create_context() for h in self.all_recref_formset_handlers())
        )
        for c in context_list:
            context.update(c)
        return context

    def is_invalid(self):
        form_formsets = (f for f in self.every_form_formset if f.has_changed())
        return any_invalid_with_log(form_formsets)

    def prepare_cleaned_data(self):
        for f in self.every_form_formset:
            f.is_valid()
