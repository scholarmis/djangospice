from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar
from urllib.parse import urlencode

from django.apps import apps
from django.http import HttpRequest
from django.urls import reverse

from djangospice.html.component import HTMLComponent
from djangospice.response.response import Response

from .actions import Actions
from .exceptions import WidgetNotVisible
from .metaclass import WidgetMetaclass, WidgetOptions


class BaseWidget(HTMLComponent, ABC, metaclass=WidgetMetaclass):
    """
    Base class for all widgets.

    Responsibilities
    ----------------
    - Maintain widget state.
    - Expose lifecycle hooks.
    - Build responses.
    - Provide metadata.

    Rendering is delegated to WidgetRenderer.
    Execution is delegated to WidgetExecutor.
    """

    NAMESPACE = "djangospice_widget"

    actions: ClassVar[Actions] = Actions()

    _meta: WidgetOptions

    def __init__(self, request: HttpRequest | None = None, **kwargs: Any) -> None:
        super().__init__(kwargs=kwargs)

        self.request = request

        self.template_name = (
            self._meta.template_name
            or self.template_name
        )

    # ==================================================================
    # Lifecycle
    # ==================================================================

    def initialize(self) -> None:
        """
        Called immediately after widget construction.
        """

    def configure(self) -> None:
        """
        Configure widget state.
        """

    def configure_htmx(self) -> None:
        """
        Configure default HTMX behaviour.
        """

        if self.lazy:
            (
                self.htmx
                .get(self.endpoint)
                .trigger_on("load")
                .target_to("this")
                .swap_to("outerHTML")
            )

        if self.refreshable and self.refresh_interval:

            trigger = self.htmx.trigger or "load"

            (
                self.htmx
                .trigger_on(
                    f"{trigger}, every {self.refresh_interval}s"
                )
                .target_to("this")
            )

    def authorize(self) -> None:
        """
        Raise if this widget cannot be accessed.
        """

        if not self.visible():
            raise WidgetNotVisible

    # ==================================================================
    # Metadata
    # ==================================================================

    @property
    def name(self) -> str:
        return self._meta.name

    @property
    def app_label(self) -> str:
        return self._meta.app_label

    @property
    def title(self) -> str:
        return self._meta.title

    @property
    def description(self) -> str:
        return self._meta.description

    @property
    def group(self) -> str | None:
        return self._meta.group

    @property
    def enabled(self) -> bool:
        return self._meta.enabled

    @property
    def permission(self) -> str | None:
        return self._meta.permission

    @property
    def priority(self) -> int:
        return self._meta.priority

    @property
    def lazy(self) -> bool:
        return self._meta.lazy

    @property
    def refreshable(self) -> bool:
        return self._meta.refreshable

    @property
    def refresh_interval(self) -> int | None:
        return self._meta.refresh_interval

    @property
    def cache_timeout(self) -> int | None:
        return self._meta.cache_timeout

    @property
    def cache_enabled(self) -> bool:
        return self.cache_timeout is not None

    # ==================================================================
    # Runtime
    # ==================================================================

    @property
    def user(self):
        return getattr(self.request, "user", None)

    @property
    def widget_key(self) -> str:
        return (
            f"{self.app_label}.{self.name}"
            if self.app_label
            else self.name
        )

    @property
    def endpoint(self) -> str:
        """
        HTMX endpoint for this widget.
        """

        url = reverse(
            self.NAMESPACE,
            kwargs={
                "app_label": self.app_label,
                "name": self.name,
            },
        )

        params = {
            k: v
            for k, v in self.kwargs.items()
            if k != "id"
        }

        return (
            f"{url}?{urlencode(params)}"
            if params
            else url
        )

    @property
    def is_lazy_fetch(self) -> bool:
        """
        True when the current request originates from this widget.
        """

        if not self.request:
            return False

        if self.request.headers.get("HX-Request") != "true":
            return False

        match = self.request.resolver_match

        return (
            match
            and match.view_name == self.NAMESPACE
            and match.kwargs.get("app_label") == self.app_label
            and match.kwargs.get("name") == self.name
        )

    # ==================================================================
    # Visibility
    # ==================================================================

    def visible(self) -> bool:

        if not self.enabled:
            return False

        if self.permission:

            user = self.user

            if not user or not user.is_authenticated:
                return False

            if not user.has_perm(self.permission):
                return False

        return self.is_visible()

    def is_visible(self) -> bool:
        """
        Override for application-specific visibility rules.
        """
        return True

    # ==================================================================
    # Cache
    # ==================================================================

    def should_cache(self) -> bool:
        return self.cache_enabled

    def cache_key(self) -> str:

        user = self.user

        identifier = (
            str(user.pk)
            if user and user.is_authenticated
            else "anonymous"
        )

        return (
            f"{self.NAMESPACE}:"
            f"{self.widget_key}:"
            f"{identifier}:"
            f"{self._generate_state_hash()}"
        )

    # ==================================================================
    # Rendering
    # ==================================================================

    def get_context(self) -> dict[str, Any]:

        context = super().get_context()

        context.update(
            widget=self,
            request=self.request,
        )

        return context

    def response(self) -> Response:
        """
        Default widget response.
        """

        return Response.make(
            self.template_name,
            **self.get_context(),
        )

    # ==================================================================
    # HTTP Handlers
    #
    # WidgetExecutor chooses which handler to call.
    # These methods never receive a request parameter because the request
    # is already bound to the widget.
    # ==================================================================

    def get(self) -> Response:
        return self.response()

    def post(self) -> Response:
        return self.method_not_allowed()

    def put(self) -> Response:
        return self.method_not_allowed()

    def patch(self) -> Response:
        return self.method_not_allowed()

    def delete(self) -> Response:
        return self.method_not_allowed()

    def method_not_allowed(self) -> Response:
        return Response.empty(status=405)