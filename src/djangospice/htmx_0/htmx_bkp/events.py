import json
from django.http import HttpResponse


class HTMXEvent:
    """Represents a single HTMX event instance with auto-serialization."""
    
    def __init__(self, name, **kwargs):
        self.name = name
        self.data = self._prepare_data(kwargs)

    def _prepare_data(self, data):
        """
        Recursively introspects dictionary values to trigger to_dict() 
        on models or clean up nested structures.
        """
        if isinstance(data, dict):
            return {k: self._prepare_data(v) for k, v in data.items()}
        
        if isinstance(data, (list, tuple, set)):
            return [self._prepare_data(item) for item in data]

        # Trigger the auto-serialization if the object supports it
        if hasattr(data, 'to_dict') and callable(getattr(data, 'to_dict')):
            return data.to_dict()

        return data

    def to_dict(self):
        """Returns the event in the format expected by HX-Trigger."""
        return {self.name: self.data}
    

class HTMXRedirectEvent(HTMXEvent):
    """Specific event to trigger a client-side redirect via HX-Redirect."""
    def __init__(self, url):
        super().__init__("hxRedirect", url=url)


class HTMXRefreshEvent(HTMXEvent):
    """Specific event to trigger a full page reload."""
    def __init__(self):
        super().__init__("hxRefresh")


class HTMXEventResponse:
    """Wraps a Django response to collect and attach HTMXEvent instances."""
    def __init__(self, response=None, status=204):
        self.response = response or HttpResponse(status=status)
        self.events = {}

    def add(self, *event_instances):
        """Pass one or more HTMXEvent instances."""
        for event in event_instances:
            if isinstance(event, HTMXEvent):
                self.events.update(event.to_dict())
            elif isinstance(event, dict):
                self.events.update(event)
        return self

    def _merge_existing_headers(self):
        """Ensures we don't overwrite existing HX-Trigger headers."""
        existing = self.response.get("HX-Trigger")
        if existing:
            try:
                current = json.loads(existing)
                if isinstance(current, str):
                    current = {current: {}}
                self.events = {**current, **self.events}
            except json.JSONDecodeError:
                self.events = {existing: {}, **self.events}

    def render(self):
        """Finalizes the response with the HX-Trigger header."""
        self._merge_existing_headers()
        if self.events:
            self.response["HX-Trigger"] = json.dumps(self.events)
        return self.response


class HTMXEventMixin:
    """Provides a concise interface for emitting HTMX events from views."""
    htmx_events = None # Use None to avoid mutable list issues
    
    def get_htmx_events(self):
        """Override this for dynamic events (e.g. including object IDs)."""
        return self.htmx_events or []

    def dispatch_events(self, *events, response=None, status=204):
        """Explicitly send events immediately."""
        res = response or HttpResponse(status=status)
        # Using your Wrapper class logic
        return HTMXEventResponse(res).add(*events).render()
    
    def emit_events(self, response=None):
        """Automatically tags a response with events from the class attributes."""
        events = self.get_htmx_events()
        if events:
            return self.dispatch_events(*events, response=response)
        return response  
    
    def redirect_to(self, url, response=None):
        """Helper to return a response that triggers a client-side redirect."""
        return self.dispatch_events(HTMXRedirectEvent(url), response=response)

    def refresh_page(self, response=None):
        """Helper to return a response that triggers a full page refresh."""
        return self.dispatch_events(HTMXRefreshEvent(), response=response)
    

def event(name, **kwargs):
    """
    Factory function to create an HTMXEvent instance.
    Usage: event("nameChanged", id=1, name="John")
    """
    return HTMXEvent(name, **kwargs)


def emit_event(name, data=None, response=None, status=204):
    """Quick helper for a single event response."""
    e = event(name, **(data or {}))
    return HTMXEventResponse(response, status).add(e).render()


def emit_events(*event_instances, response=None, status=204):
    """
    Quick helper for multiple event instances.
    Usage: emit_events(event('A'), event('B'), response=res)
    """
    return HTMXEventResponse(response, status).add(*event_instances).render()


def emit_refresh_data(response=None):
    return emit_event("refreshData", response=response)


def emit_close_modal(response=None):
    return emit_event("closeModal", response=response)


def emit_refresh_tab(response=None):
    return emit_event("refreshTab", response=response)


def emit_request_completed(response=None):
    return emit_event("requestCompleted", response=response)


def emit_action_completed(response=None):
    return emit_event("actionPerformed", response=response)


def emit_form_submitted(response=None):
    return emit_event("formSubmitted", response=response)