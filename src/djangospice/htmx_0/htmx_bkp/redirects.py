import json
from djarf.urls import safe_reverse
from .response import HTMXResponse



def htmx_redirect(url, **kwargs):
    """
    Shortcut for HTMX-native redirects (HX-Location).
    Usage: return htmx_redirect('/dashboard/')
    """
    return HTMXResponse.redirect(url, refresh=False, **kwargs)


def htmx_refresh(url, **kwargs):
    """
    Shortcut for full-page refreshes (HX-Redirect).
    Usage: return htmx_refresh('/login/')
    """
    return HTMXResponse.redirect(url, refresh=True, **kwargs)


def htmx_safe_redirect(view_name, app_name=None, args=None, **kwargs):
    url = safe_reverse(view_name, app_name, args)
    return htmx_redirect(url, **kwargs)


def htmx_safe_refresh(view_name, app_name=None, args=None, **kwargs):
    url = safe_reverse(view_name, app_name, args)
    return htmx_refresh(url, **kwargs)


def htmx_data_refresh(request, target="#htmx-data-container", swap="innerHTML"):
    return htmx_redirect(url=request.path, target=target, swap=swap)
    
