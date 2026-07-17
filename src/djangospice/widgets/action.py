from abc import ABC, abstractmethod

from django.http import HttpRequest

from djangospice.response.response import Response


class WidgetAction(ABC):

    name: str = ""
    
    label: str = ""

    method: str = "POST"

    permission: str | None = None

    confirm: str | None = None

    icon: str | None = None
    
    is_visible: bool = True
    is_danger: bool = False
    is_primary: bool = False
    
    def can_confirm(self):
        return True if self.confirm else False

    def get_label(self):
        return self.label or self.name.replace("_", " ").title()

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "label": self.get_label(),
            "icon": self.icon,
            "confirm": self.confirm,
            "can_confirm": self.can_confirm(),
            "open_tab": self.open_tab,
            "is_danger": self.is_danger,
            "is_primary": self.is_primary,
            "order": self.order,
        }


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
        
        
        
