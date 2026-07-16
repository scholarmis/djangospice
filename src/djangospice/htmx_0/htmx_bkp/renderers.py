import json
from .response import HTMXResponse


def htmx_render(request, template, context=None, **kwargs):
    """
    Renders a partial with stateless Message objects.
    'alerts' can be a string, a Message object, or a list of either.
    """

    return HTMXResponse.render(
        request, 
        template, 
        context, 
        **kwargs
    )


def htmx_partial(request, extra_partials, **kwargs):
    """
    Shortcut for updating OOB fragments WITHOUT changing the main target.
    Usage: return htmx_partial(request, ['sidebar.html'])
    """
    return HTMXResponse.render(request, template=None, extra_partials=extra_partials, **kwargs)
