from django.views.generic import View, DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import TemplateResponseMixin
from django_filters.views import FilterView
from djarf.forms.imports import ImportExcelForm
from djarf.requests import is_htmx
from djarf.files.helpers import save_uploaded_file
from djarf.htmx.download import render_download_launcher
from djarf.htmx.events import emit_refresh_data
from djarf.htmx.progress import render_task_launcher
from djarf.htmx.tasks import import_model_resource, export_model_resource
from djarf.htmx.renderers import htmx_render
from djarf.htmx.alerts import htmx_alert_success, htmx_alert_error
from .mixins import HTMXFormMixin, HTMXListMixin, HTMXPaginationMixin, HTMXSearchMixin


class HTMXView(TemplateResponseMixin, View):
    htmx_template_name = None 

    def get_template_names(self):
        if is_htmx(self.request):
            return [self.htmx_template_name]
        return [self.template_name]

    def render_to_response(self, context, **response_kwargs):
        if is_htmx(self.request):
            return htmx_render(self.request, self.htmx_template_name, context)
        return super().render_to_response(context, **response_kwargs)
    
    def alert_success(self, text):
        return htmx_alert_success(self.request.user.id, text)
    
    def alert_error(self, text):
        return htmx_alert_error(self.request.user.id, text)


class HTMXListView(HTMXListMixin, HTMXPaginationMixin, ListView):
    pass


class HTMXFilterView(HTMXListMixin, HTMXPaginationMixin, FilterView):
    pass


class HTMXSearchView(HTMXSearchMixin, HTMXFilterView):
    htmx_template_base_path = "search"
    
    def get_queryset(self):
        return self.apply_search(super().get_queryset())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.get_search_query()
        context.update({
            "placeholder": self.placeholder,
            "query": query, 
            "has_query": bool(query)
        })
        return context
    
    
class HTMXDetailView(DetailView, HTMXView):
    pass


class HTMXDeleteView(SingleObjectMixin, View):
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return emit_refresh_data()

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
     
    
class HTMXImportView(HTMXFormMixin, FormView):
    export_trigger_param = "_export"
    form_class = ImportExcelForm
    resource_class = None  # Expected to be a django-import-export Resource class

    def get(self, request, *args,  **kwargs):
        export = request.GET.get(self.export_trigger_param)
        
        if export == "template":
            resource = self.resource_class(**kwargs)
            return resource.export()    
        return super().get(request, *args, **kwargs)
    
    def get_resource_kwargs(self):
        return {}
    
    def get_context_data(self, **kwargs):
        """
        Injects the resolved cancel_url into the template context.
        """
        context = super().get_context_data(**kwargs)
        context["export_trigger_param"] = self.export_trigger_param
        context["is_htmx"] = is_htmx(self.request)
        context["http_referer"] = self.request.META.get("HTTP_REFERER")
        return context

    def get_resource_path(self):
        """
        Helper to return the full python path of the resource class for background tasks.
        """
        if not self.resource_class:
            raise AttributeError(f"{self.__class__.__name__} requires 'resource_class' to be defined.")
        return f"{self.resource_class.__module__}.{self.resource_class.__name__}"

    def import_resource(self, file_path, action_url):
        """
        Triggers the asynchronous import task.
        """
        user_id = self.request.user.id
        resource_path = self.get_resource_path()
        kwargs = self.get_resource_kwargs()
        # Ensure your task is set up to handle these specific arguments
        return import_model_resource.delay(user_id, resource_path, file_path, action_url, **kwargs)
    
    def export_resource(self):
        """
        Triggers the asynchronous export task or returns a download response.
        """
        user_id = self.request.user.id
        resource_path = self.get_resource_path()
        export_data = False

        kwargs = self.get_resource_kwargs()
        
        export_model_resource.delay(user_id, resource_path, export_data, **kwargs)
        
        # For HTMX, you might want to return a notification that the export has started
        # Or redirect back to the current page.
        return self.render_to_response(self.get_context_data())
        
    def form_valid(self, form):
        """
        Handles the file upload, saves it temporarily, and starts the import task.
        """
        file = form.cleaned_data["file"]
        
        # Save file to a temporary location accessible by the celery worker
        file_path = save_uploaded_file(file)
        
        # Get the resolved success URL to redirect the user after the task completes
        success_url = self.get_success_url()

        # Trigger the task logic
        task = self.import_resource(file_path, success_url)
        
        # Provide UI feedback (e.g., progress bar or 'Processing...' message)
        feedback = "File import is processing"
        
        return render_task_launcher(self.request, task.id, feedback)
    

class HTMXExportView(View): 
    resource_class = None
    
    def get_resource_kwargs(self):
        return {}
    
    def get_resource_path(self):
        """
        Helper to return the full python path of the resource class for background tasks.
        """
        if not self.resource_class:
            raise AttributeError(f"{self.__class__.__name__} requires 'resource_class' to be defined.")
        return f"{self.resource_class.__module__}.{self.resource_class.__name__}"
    
    def export_resource(self):
        """
        Triggers the asynchronous export task or returns a download response.
        """
        user_id = self.request.user.id
        resource_path = self.get_resource_path()
        export_data = True

        kwargs = self.get_resource_kwargs()
        
        export_model_resource.delay(user_id, resource_path, export_data, **kwargs)
        
   
    def get(self, request, *args, **kwargs):
        self.export_resource()
        return render_download_launcher(request)
        

    