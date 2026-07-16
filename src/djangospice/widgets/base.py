from __future__ import annotations

from abc import ABC
from typing import Any
from urllib.parse import urlencode
from dataclasses import dataclass, fields
from django.apps import apps
from django.http import HttpRequest
from django.urls import reverse
from djangospice.html.component import HTMLComponent

from .utils import slugify


@dataclass
class WidgetOptions:
    """
    Stores the declarative configuration metadata for a widget.
    Automatically handles smart defaults if values are omitted.
    """
    name: str
    title: str
    app_label: str = "" 
    description: str = ""
    template_name: str = ""
    group: str | None = None
    permission: str | None = None
    enabled: bool = True
    priority: int = 100
    cache_timeout: int | None = None
    lazy: bool = False
    refreshable: bool = False
    refresh_interval: int | None = None

    @classmethod
    def from_meta(cls, meta: type | None, class_name: str, module_path: str) -> WidgetOptions:
        """
        Factory method to build options from an inner Meta class.
        Applies automatic defaults for name, title, template_name, and app_label.
        """
        kwargs = {}
        
        # Extract explicitly defined values from the Meta class
        if meta:
            for f in fields(cls):
                if hasattr(meta, f.name):
                    kwargs[f.name] = getattr(meta, f.name)

        # 1. Resolve Django App Label
        if not kwargs.get("app_label"):
            kwargs["app_label"] = cls._resolve_app_label(module_path)

        # 2. Auto-generate Name
        if not kwargs.get("name"):
            kwargs["name"] = slugify(class_name) if class_name else ""
            
        # 3. Auto-generate Title
        if not kwargs.get("title"):
            kwargs["title"] = kwargs["name"].replace("_", " ").title()
            
        return cls(**kwargs)

    @classmethod
    def _resolve_app_label(cls, module_path: str) -> str:
        """
        Resolves the Django app label from the widget's module path.
        """
        try:
            for app_config in apps.get_app_configs():
                if module_path.startswith(app_config.name):
                    return app_config.label
        except Exception:
            pass
        
        parts = module_path.split('.')
        return parts[0] if parts else ""


class WidgetMetaclass(type):
    """
    Metaclass for Widget. Intercepts class creation to parse the 
    inner `Meta` class and attach the `WidgetOptions` dataclass.
    """
    def __new__(cls, name: str, bases: tuple, attrs: dict) -> type:
        new_class = super().__new__(cls, name, bases, attrs)
        
        if bases == (object,):
            return new_class

        meta = attrs.pop("Meta", None)
        module_path = attrs.get("__module__", "")

        new_class._meta = WidgetOptions.from_meta(meta, name, module_path)
        return new_class
    

class BaseWidget(HTMLComponent, ABC, metaclass=WidgetMetaclass):
    """
    Base class for all widgets.
    Configuration should be defined within an inner `Meta` class.
    """
    
    URL_NAME = "djangospice:widget"
    _meta: WidgetOptions 

    def __init__(self, request: HttpRequest | None = None, **kwargs: Any) -> None:
        super().__init__(kwargs=kwargs)
        self.request = request
        self.template_name = getattr(self._meta, "template_name", self.template_name)
        self.configure()
        
    def configure(self) -> None:
        if self.lazy:
            self.htmx.request("get", self.endpoint) \
                     .trigger_on("load") \
                     .swap_to("outerHTML") \
                     .target_to("this")

        if getattr(self, "refreshable", False) and getattr(self, "refresh_interval", None):
            trigger = self.htmx.trigger or "load"
            self.htmx.trigger_on(f"{trigger}, every {self.refresh_interval}s")
            self.htmx.target_to("this")

    # ----------------------------------------------------------
    # Properties & Permissions
    # ----------------------------------------------------------
    
    @property
    def name(self) -> str: return self._meta.name
    @property
    def app_label(self) -> str: return self._meta.app_label
    @property
    def title(self) -> str: return self._meta.title
    @property
    def description(self) -> str: return self._meta.description
    @property
    def group(self) -> str | None: return self._meta.group
    @property
    def enabled(self) -> bool: return self._meta.enabled
    @property
    def priority(self) -> int: return self._meta.priority
    @property
    def permission(self) -> str | None: return self._meta.permission
    @property
    def cache_timeout(self) -> int: return self._meta.cache_timeout
    @property
    def cache_enabled(self) -> bool: return self._meta.cache_timeout is not None
    @property
    def lazy(self) -> bool: return self._meta.lazy

    @property
    def user(self) -> Any | None:
        return getattr(self.request, "user", None) if self.request else None
    
    @property
    def widget_key(self) -> str:
        """
        Returns a unique identifier (e.g. 'polls.recent_polls') 
        to guarantee registry safety.
        """
        return f"{self.app_label}.{self.name}" if self.app_label else self.name

    @property
    def endpoint(self) -> str:
        """Calculates namespaced endpoint coordinates matching /app_label/widgets/name/"""
        base_url = reverse(
            self.URL_NAME, 
            kwargs={"app_label": self.app_label, "name": self.name}
        )
        query_kwargs = {k: v for k, v in self.kwargs.items() if k != "id"}
        return f"{base_url}?{urlencode(query_kwargs)}" if query_kwargs else base_url

    @property
    def is_lazy_fetch(self) -> bool:
        """Determines if the inbound channel matches this exact execution block."""
        if not self.request:
            return False
        is_htmx = self.request.headers.get("HX-Request") == "true"
        rm = self.request.resolver_match
        
        is_endpoint = (
            rm and 
            rm.view_name == self.URL_NAME and 
            rm.kwargs.get("app_label") == self.app_label and
            rm.kwargs.get("name") == self.name
        )
        return is_htmx and is_endpoint
    
    def visible(self) -> bool:
        if not self.enabled:
            return False
        if self.permission:
            if not self.user or not self.user.is_authenticated:
                return False
            if not getattr(self.user, "has_perm", lambda p: False)(self.permission):
                return False
        return self.is_visible()

    def is_visible(self) -> bool:
        return True

    def should_cache(self) -> bool:
        return self.cache_enabled

    def cache_key(self) -> str:
        user = self.user
        identifier = str(user.pk) if user and user.is_authenticated else "anonymous"
        digest = self._generate_state_hash()
        return f"widget:{self.widget_key}:{identifier}:{digest}"

    def get_context(self) -> dict[str, Any]:
        ctx = super().get_context()
        ctx["widget"] = self
        ctx["request"] = self.request
        return ctx