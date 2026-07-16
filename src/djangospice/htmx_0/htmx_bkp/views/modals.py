from django.views.generic import CreateView, UpdateView, DeleteView
from djarf.htmx.events import emit_refresh_data
from djarf.templates import get_template_name
from djarf.requests import is_htmx
from djarf.htmx.renderers import htmx_render
from djarf.htmx.apps import app_name
from .generic import HTMXView
from .mixins import HTMXFormMixin, HTMXModalMixin


class HTMXModal(HTMXModalMixin, HTMXView):
    htmx_template_name = get_template_name("modal/modal.html", app_name)
    modal_template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.modal_template_name:
            raise ValueError(f"{self.__class__.__name__} requires modal_template_name.")
        context["modal_template_name"] = self.modal_template_name
        context["modal"] = self.get_modal_config()
        return context

    def render_to_response(self, context, **response_kwargs):
        return htmx_render(self.request, self.htmx_template_name, context)
     

class HTMXFormModal(HTMXModal, HTMXFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context: 
            context['form'] = self.get_form()
        return context
    
    def get_success_url(self): 
        return self.request.path


class HTMXCreateModal(HTMXFormModal, CreateView):
    pass


class HTMXUpdateModal(HTMXFormModal, UpdateView):
    pass
    

class HTMXDeleteModal(HTMXModal, DeleteView):
    modal_title = "Confirm Deletion"
    save_button_text = "Yes, Delete"
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if is_htmx(self.request):
           return emit_refresh_data()
        return super().delete(request, *args, **kwargs)

