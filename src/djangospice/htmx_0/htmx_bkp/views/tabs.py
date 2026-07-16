from typing import Any, Dict, List, Type
from django.http import HttpRequest
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import View, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import render
from djarf.htmx.alerts import htmx_alert_error
from djarf.requests import is_htmx
from .forms import HTMXCreateView, HTMXUpdateView
from .mixins import HTMXTabFormMixin
from .generic import HTMXDeleteView, HTMXView


class HTMXTabView(UserPassesTestMixin, HTMXView):
    """The interface all tabs must follow."""
    tab_name = ""
    tab_label = ""
    is_primary = False
    permission_required = None
    context_meta_name = "tab_meta"

    def test_func(self):
        if self.permission_required:
            return self.request.user.has_perm(self.permission_required)
        return True

    @classmethod
    def get_tab_metadata(cls):
        name = cls.tab_name
        label = cls.tab_label
        
        if name and not label:
            label = name.replace('_', ' ').replace('-', ' ').title()

        elif label and not name:
            name = slugify(label).replace('-', '_')

        return {
            "name": name,
            "label": label,
            "is_primary": cls.is_primary,
            "class": cls,
            "perm": cls.permission_required
        }
        
    def get_context_data(self, **kwargs):
        # Start with existing context (from HTMXView/TemplateView)
        context = super().get_context_data(**kwargs)
        # Add the tab metadata for the current active tab
        context[self.context_meta_name] = self.get_tab_metadata()
        return context
        

class HTMXTemplateTabView(HTMXTabView):
    """Object-less: For general info, stats, or global settings."""
    pass


class HTMXDetailTabView(HTMXTabView, DetailView):
    """Object-ful: For specific records (requires a PK)."""
    model = None
    
    
class HTMXUpdateTabView(HTMXTabFormMixin, HTMXTabView, HTMXUpdateView):
    pass


class HTMXCreateTabView(HTMXTabFormMixin, HTMXTabView,  HTMXCreateView):
    pass
    
          
class HTMXDeleteTabView(HTMXTabFormMixin, HTMXDeleteView):
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            return self.emit_refresh_tab()
        except Exception as e:
            htmx_alert_error(self.request.user.pk, str(e))
            return self.emit_refresh_tab()
        

class HTMXTabContainerView(View):
    template_name = None
    tab_classes: List[Type[HTMXTabView]] = []
    param_name = "tab"
    title = None
    model = None

    # ------------------------------------------------------------------
    # TAB RESOLUTION
    # ------------------------------------------------------------------

    @classmethod
    def get_tab_session_key(cls):
        return f"active_tab_{cls.__name__}"

    @classmethod
    def get_active_tab_name(cls, request: HttpRequest) -> str:
        session_key = cls.get_tab_session_key()

        tab_name = request.POST.get(cls.param_name)

        if not tab_name:
            tab_name = request.GET.get(cls.param_name)

        if not tab_name:
            tab_name = request.session.get(session_key)

        if not tab_name and cls.tab_classes:
            visible_tabs = [c.get_tab_metadata() for c in cls.tab_classes]
            active_tab = next((t for t in visible_tabs if t["is_primary"]), visible_tabs[0])
            tab_name = active_tab["name"]

        return tab_name

    # ------------------------------------------------------------------
    # OVERRIDABLE HOOKS
    # ------------------------------------------------------------------

    def get_tab_classes(self) -> List[HTMXTabView]:
        """
        Allows subclasses to dynamically control which tabs appear.
        """
        return list(self.tab_classes)

    def get_container_context(self) -> Dict:
        """
        Extra context that subclasses can inject into the container template.
        """
        return {}

    def get_context_data(self, **kwargs) -> Dict:
        """
        Final context builder for the container template.
        """
        context = {
            "title": self.title
        }
        context.update(kwargs)
        context.update(self.get_container_context())
        return context

    # ------------------------------------------------------------------
    # OBJECT RESOLUTION
    # ------------------------------------------------------------------

    def get_parent_object(self) -> Any:
        if not self.model:
            return None

        mixer = SingleObjectMixin()
        mixer.model = self.model
        mixer.kwargs = self.kwargs
        return mixer.get_object()

    # ------------------------------------------------------------------
    # TAB FILTERING
    # ------------------------------------------------------------------

    def get_visible_tabs(self, request) -> List[Dict]:
        """
        Filters tab classes based on permissions.
        """
        tabs = []

        for cls in self.get_tab_classes():
            if not cls.permission_required or request.user.has_perm(cls.permission_required):
                tabs.append(cls.get_tab_metadata())

        return tabs

    # ------------------------------------------------------------------
    # TAB STATE
    # ------------------------------------------------------------------

    def resolve_active_tab(self, request, visible_tabs: List[Dict]) -> Dict:
        tab_name = self.get_active_tab_name(request)

        active_tab = next((t for t in visible_tabs if t["name"] == tab_name), None)

        if not active_tab:
            active_tab = next((t for t in visible_tabs if t["is_primary"]), visible_tabs[0])

        request.session[self.get_tab_session_key()] = active_tab["name"]

        return active_tab

    # ------------------------------------------------------------------
    # SUB VIEW EXECUTION
    # ------------------------------------------------------------------

    def prepare_sub_view_context(self, request, active_tab_class, parent_object, **kwargs):
        sub_view: HTMXTabView = active_tab_class()
        sub_view.setup(request, **kwargs)

        if hasattr(sub_view, "get_object"):
            sub_view.object = parent_object or sub_view.get_object()

        if not sub_view.test_func():
            raise PermissionDenied

        return sub_view.get_context_data(**kwargs)

    # ------------------------------------------------------------------
    # MAIN HANDLER
    # ------------------------------------------------------------------

    def get(self, request, *args, **kwargs):

        visible_tabs = self.get_visible_tabs(request)

        if not visible_tabs:
            raise PermissionDenied("No authorized tabs available.")

        parent_object = self.get_parent_object()

        active_tab = self.resolve_active_tab(request, visible_tabs)
        active_class = active_tab["class"]

        # HTMX partial
        if is_htmx(request):
            return active_class.as_view()(request, *args, **kwargs)

        # full page
        tab_context = self.prepare_sub_view_context(
            request, active_class, parent_object, **kwargs
        )

        session_key = self.get_tab_session_key()

        orchestrator_context = self.get_context_data(
            **tab_context,
            container_object=parent_object,
            tabs=visible_tabs,
            active_tab=active_tab,
            active_tab_session_key=session_key,
            tab_param=self.param_name,
        )

        return render(request, self.template_name, orchestrator_context)