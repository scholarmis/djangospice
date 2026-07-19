from abc import ABC, abstractmethod
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied

from djangospice.response.response import Response

from .widget import BaseWidget
from .context import ActionContext


class BaseDispatcher(ABC):
    
    def __init__(self, widget: BaseWidget, request: HttpRequest):
        self.widget = widget
        self.request = request
        
    @abstractmethod
    def can_dispatch(self) -> bool:
        pass
    
    @abstractmethod
    def dispatch(self) -> Response:
        pass
    
    
class ActionDispatcher(BaseDispatcher):
    """
    Dispatches widget actions.
    """

    parameter = "action"

    def can_dispatch(self) -> bool:
        return self.parameter in self.request.GET or self.parameter in self.request.POST

    def dispatch(self) -> Response:

        name = (
            self.request.POST.get(self.parameter)
            or self.request.GET.get(self.parameter)
        )

        action = self.widget.actions.require(name)

        context = ActionContext(
            widget=self.widget,
            request=self.request,
        )

        if not action.enabled(context):
            raise PermissionDenied(
                f"Action '{name}' is disabled."
            )

        action.authorize(context)

        action.before_execute(context)

        response = action.execute(context)

        action.after_execute(context)

        return response
    
   
class MethodDispatcher(BaseDispatcher):
    """
    Dispatches HTTP methods.
    """

    def can_dispatch(self) -> bool:
        return True

    def dispatch(self) -> Response:

        handler = getattr(self.widget, self.request.method.lower(), None)

        if handler is None:
            return self.widget.method_not_allowed()

        return handler()