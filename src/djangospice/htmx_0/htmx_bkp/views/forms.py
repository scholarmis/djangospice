from django.views.generic import CreateView, UpdateView
from .generic import HTMXView
from .mixins import HTMXFormMixin


class HTMXFormView(HTMXView, HTMXFormMixin):
    """Base for any view that contains a form."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context
    
    
class HTMXCreateView(HTMXFormView, CreateView):

    def get_success_url(self):
        return self.request.path
    
    
class HTMXUpdateView(HTMXFormView, UpdateView):

    def get_success_url(self):
        return self.request.path
    

    
class CreateUpdateMixin:
    title = "Input Form"

    def get_title(self):
        return self.title
    
    def get_cancel_url(self):
        return self.request.META.get("HTTP_REFERER")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["cancel_url"] = self.get_cancel_url()
        return context
    