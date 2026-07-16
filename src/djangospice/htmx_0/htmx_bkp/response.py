import json
from django.template.loader import render_to_string
from django.http import HttpResponse


class HTMXResponse:
    
    @staticmethod
    def render(request, template=None, context=None, extra_partials=None, **kwargs ):
        context = context or {}
        html_parts = []

        if template:
            html_parts.append(render_to_string(template, context, request=request))

        if extra_partials:
            for pt in extra_partials:
                html_parts.append(render_to_string(pt, context, request=request))

        response = HttpResponse("".join(html_parts))
        return HTMXResponse._add_headers(response, **kwargs)

    @staticmethod
    def redirect(url, target=None, swap=None, refresh=False, **kwargs):
        """
        Handles navigation. 
        - refresh=True: Full browser reload (HX-Redirect).
        - refresh=False: AJAX navigation (HX-Location).
        """
        response = HttpResponse()
        if refresh:
            response["HX-Redirect"] = url
        else:
            location = {"path": url}
            if target: location["target"] = target
            if swap: location["swap"] = swap
            response["HX-Location"] = json.dumps(location)
            
        return HTMXResponse._add_headers(response, **kwargs)

    @staticmethod
    def _add_headers(
        response, 
        retarget=None, 
        reswap=None, 
        trigger=None, 
        push_url=None, 
        replace_url=None,
        trigger_after_settle=None,
        trigger_after_swap=None
    ):
        """Attaches all supported HTMX control headers."""
        
        # Target & Swap overrides
        if retarget: response["HX-Retarget"] = retarget
        if reswap: response["HX-Reswap"] = reswap
        
        # History Management
        if push_url:
            response["HX-Push-Url"] = "true" if push_url is True else push_url
        if replace_url:
            response["HX-Replace-Url"] = "true" if replace_url is True else replace_url

        # Event Triggers (Immediate, After Settle, After Swap)
        if trigger:
            response["HX-Trigger"] = json.dumps(trigger) if isinstance(trigger, dict) else trigger
        if trigger_after_settle:
            response["HX-Trigger-After-Settle"] = json.dumps(trigger_after_settle) if isinstance(trigger_after_settle, dict) else trigger_after_settle
        if trigger_after_swap:
            response["HX-Trigger-After-Swap"] = json.dumps(trigger_after_swap) if isinstance(trigger_after_swap, dict) else trigger_after_swap
            
        return response


class HTMXAlert:
    text = None
    tags = None
    
    
    def __init__(self, text, tags=None):
        self.text = text
        self.tags = tags
        
        
    def __str__(self):
        return self.text
