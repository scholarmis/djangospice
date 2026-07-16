from typing import Any
from django import template
from django.utils.safestring import SafeString

from djangospice.widgets.registry import WidgetRegistry
from djangospice.widgets.renderer import WidgetRenderer
from djangospice.widgets.exceptions import WidgetNotVisible

register = template.Library()


@register.simple_tag(takes_context=True)
def render_widget(context: template.Context, name: str, **kwargs: Any) -> SafeString:
    request = context.get("request")
    
    try:
        widget_class = WidgetRegistry.get(name)
    except KeyError:
        return SafeString(f"")

    widget_instance = widget_class(request=request, **kwargs)

    try:
        renderer = WidgetRenderer(widget_instance)
        return renderer.render()
    except WidgetNotVisible:
        return SafeString("")