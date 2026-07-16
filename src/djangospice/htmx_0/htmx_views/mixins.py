from __future__ import annotations
    
from djangospice.htmx_response.response import HTMXResponse
from djangospice.htmx_response.requests import (
    is_boosted,
    is_htmx,
    get_current_url,
    get_target,
    get_trigger,
    get_trigger_name,
)



class HTMXMixin:
    """
    Base mixin for HTMX-enabled class-based views.

    Provides convenient access to HTMX request information and a factory
    for creating HTMX response.
    """

    response_class = HTMXResponse

    # ------------------------------------------------------------------
    # Response
    # ------------------------------------------------------------------

    def get_response(self, **payload) -> HTMXResponse:
        """
        Creates an HTMX response.

        Example:
            response = self.get_response(student=student)
        """
        response = self.response_class()

        if payload:
            response.payload.update(payload)

        return response

    # ------------------------------------------------------------------
    # Request Helpers
    # ------------------------------------------------------------------

    @property
    def htmx(self) -> bool:
        return is_htmx(self.request)

    @property
    def boosted(self) -> bool:
        return is_boosted(self.request)

    @property
    def htmx_target(self) -> str | None:
        return get_target(self.request)

    @property
    def htmx_trigger(self) -> str | None:
        return get_trigger(self.request)

    @property
    def htmx_trigger_name(self) -> str | None:
        return get_trigger_name(self.request)

    @property
    def htmx_current_url(self) -> str | None:
        return get_current_url(self.request)
    
     
class HTMXTemplateMixin(HTMXMixin):
    """
    Allows separate templates for HTMX requests.
    """

    htmx_template_name = None

    def get_template_names(self):

        if (self.htmx and self.htmx_template_name):
            return [self.htmx_template_name]

        return super().get_template_names()
    
    

class HTMXFormMixin(HTMXMixin):
    """
    Improves Django form behaviour for HTMX.
    """

    invalid_status_code = 422

    def form_invalid(self, form):

        response = super().form_invalid(form)

        if self.htmx:
            response.status_code = self.invalid_status_code

        return response
    
    
class HTMXObjectMixin(HTMXMixin):
    """
    Convenience helpers for object-based views.
    """

    def get_object_response(self):

        return self.get_response(
            object=self.get_object(),
        )