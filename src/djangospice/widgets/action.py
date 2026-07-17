from abc import ABC, abstractmethod

from django.http import HttpRequest

from djangospice.response.response import Response


class BaseAction(ABC):

    name: str = ""
    label: str = ""

    method: str = "POST"

    permission: str | None = None

    confirm: str | None = None

    icon: str | None = None

    def visible(self, widget) -> bool:
        return True

    def enabled(self, widget) -> bool:
        return True
    
    def authorize(self, widget):
        ...

    def before_execute(self, widget):
        ...    
    
    def after_execute(self, response):
        ...

    @abstractmethod
    def execute(self, widget, request: HttpRequest) -> Response:
        ...
        
        
        
