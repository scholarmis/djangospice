from django.db.models import Q, Value
from django.db.models.functions import Concat, Coalesce
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from djarf.htmx.events import emit_form_submitted, emit_refresh_tab
from djarf.templates import get_template_name
from djarf.requests import is_htmx
from djarf.htmx.apps import app_name


class HTMXListMixin:
    htmx_template_base_path = "dataview"
    htmx_template_name = None
    model = None 
    display_title = ""
    layouts = ["list", "grid"]
    default_layout = "list"
    primary_field = "id"
    title_fields = []
    display_fields = []
    body_field = None
    footer_field = None
    footer_label = ""
    action_label = "View"
    resource_url = None

    def get_layout_session_key(self):
        view_name = getattr(getattr(self.request, "resolver_match", None), "view_name", "") or self.__class__.__name__
        return f"htmx_layout:{view_name}"

    def get_layout(self):
        requested = self.request.POST.get("layout") or self.request.GET.get("layout")
        if requested:
            clean_layout = requested.replace(".html", "")
            if clean_layout in self.layouts:
                if hasattr(self.request, "session"):
                    self.request.session[self.get_layout_session_key()] = clean_layout
                return clean_layout
        if hasattr(self.request, "session"):
            stored = self.request.session.get(self.get_layout_session_key())
            if stored in self.layouts:
                return stored
        return self.default_layout

    def get_htmx_template_candidates(self):
        layout = self.get_layout()
        custom = get_template_name(f"{self.htmx_template_base_path}/{layout}.html", app_name)
        default = get_template_name(f"dataview/{layout}.html", app_name)
        return [custom, default] if custom != default else [default]

    def get_htmx_template_name(self):
        if self.htmx_template_name:
            return self.htmx_template_name
        
        for template_name in self.get_htmx_template_candidates():
            try:
                get_template(template_name)
                return template_name
            except TemplateDoesNotExist:
                continue
        return get_template_name(f"dataview/{self.get_layout()}.html", app_name)

    def get_ui_context(self):
        title = self.display_title or self.model._meta.verbose_name_plural.title()
        return {
            "layout": self.get_layout(),
            "htmx_template_base_path": self.htmx_template_base_path,
            "available_layouts": self.layouts,
            "primary_field": self.primary_field,
            "display_title": title,
            "resource_url": self.resource_url or "#",
            "display_config": {
                "title_fields": self.title_fields,
                "snippet_fields": self.display_fields,
                "body_field": self.body_field,
                "footer_field": self.footer_field,
                "footer_label": self.footer_label,
                "action_label": self.action_label,
            }
        }


class HTMXSearchMixin:
    query_param = "q"
    search_fields = []
    combined_fields = []
    placeholder = "Search records.."

    def get_search_query(self):
        return (self.request.POST.get(self.query_param, "").strip() or 
                self.request.GET.get(self.query_param, "").strip())

    def apply_search(self, queryset):
        query_value = self.get_search_query()
        if not query_value:
            return queryset.none()

        search_query = Q()
        fields_processed = False

        for field_group in self.combined_fields:
            fields_processed = True
            alias = "_".join(field_group) + "_combined"
            concat_args = []
            for i, field in enumerate(field_group):
                concat_args.append(Coalesce(field, Value('')))
                if i < len(field_group) - 1:
                    concat_args.append(Value(' '))
            queryset = queryset.annotate(**{alias: Concat(*concat_args)})
            search_query |= Q(**{f"{alias}__icontains": query_value})

        for field in self.search_fields:
            fields_processed = True
            search_query |= Q(**{f"{field}__icontains": query_value})

        return queryset.filter(search_query).distinct() if fields_processed else queryset.none()


class HTMXPaginationMixin:
    per_page_options = [10, 20, 50, 100]
    paginate_by = 20

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page") or self.request.POST.get("per_page")
        if per_page and str(per_page).isdigit():
            val = int(per_page)
            if val in self.per_page_options:
                return val
        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        context.update({
            "per_page_options": self.per_page_options,
            "current_per_page": self.get_paginate_by(None),
            "url_params": params.urlencode(),
        })
        return context


class HTMXFormMixin:
    
    def form_valid(self, form):
        self.object = form.save()
        if is_htmx(self.request):
            return emit_form_submitted()
        return super().form_valid(form)

    def form_invalid(self, form):
        if is_htmx(self.request):
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)
    

class HTMXModalMixin:
    modal_title = ""
    modal_size = "max-w-2xl"
    modal_icon = "fas fa-edit"
    show_save_button = True
    save_button_text = "Save"
    cancel_button_text = "Cancel"

    def get_modal_title(self):
        if self.modal_title: return self.modal_title
        verb = "View"
        if hasattr(self, 'object') and self.object:
            verb = "Update"
        return f"{verb} {self.model._meta.verbose_name.title()}"

    def get_modal_config(self):
        return {
            "title": self.get_modal_title(),
            "size": self.modal_size,
            "icon": self.modal_icon,
            "show_save": self.show_save_button,
            "save_text": self.save_button_text,
            "cancel_text": self.cancel_button_text,
        }


class HTMXTabFormMixin:
    parent_tab = None

    def get_parent_model(self):
        if self.parent_tab and hasattr(self.parent_tab, "model"):
            return self.parent_tab.model
        return None
    
    def get_action_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.parent_tab:
            # Handle metadata
            meta_name = getattr(self.parent_tab, "context_meta_name", "tab_meta")
            context[meta_name] = self.parent_tab.get_tab_metadata()
        context["action_url"] = self.get_action_url()
        return context
    
    def emit_refresh_tab(self):
        return emit_refresh_tab()
