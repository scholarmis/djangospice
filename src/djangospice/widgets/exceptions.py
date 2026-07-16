from __future__ import annotations


class WidgetError(Exception):
    """
    Base exception for the widget framework.
    """


class WidgetNotFound(WidgetError):
    """
    Raised when a widget cannot be found in the registry.
    """

    def __init__(self, widget: str) -> None:
        self.widget = widget
        super().__init__(f"Widget '{widget}' is not registered.")
        

class WidgetNotVisible(WidgetError):
    """
    Raised when attempting to render a widget that is not visible.
    """

    def __init__(self, widget: str) -> None:
        self.widget = widget
        super().__init__(f"Widget '{widget}' is not visible.")

