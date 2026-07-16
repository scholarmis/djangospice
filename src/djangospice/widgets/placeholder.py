from typing import Any

from djangospice.widgets.base import BaseWidget


class Placeholder(BaseWidget):
    
    """System level specialized element creating DOM skeleton attachment points."""
    
    class Meta:
        name = "system_htmx_placeholder"
        template_name = "widgets/placeholder.html"
        lazy = False
        cache_timeout = None


    def get_context(self) -> dict[str, Any]:
        return super().get_context() | {
            "target_id": self.kwargs.get("target_id"),
            "target_url": self.kwargs.get("target_url"),
            "target_title": self.kwargs.get("target_title"),
        }