from django.template.loader import render_to_string
from djangospice.realtime.broadcast import Broadcast
from djangospice.web.templates import get_template_name
from .response import HTMXAlert
from .apps import app_name



def get_alert_template():
    return get_template_name("alerts/alert.html", app_name)


def htmx_alert_message(user_id, text, tags):
    template_name = get_alert_template()
    message = HTMXAlert(text, tags)
    
    data = render_to_string(template_name, {
        "messages": [message]
    })
  
    Broadcast.user(user_id, data)
    

def htmx_alert_success(user_id, text):
    htmx_alert_message(user_id, text, "success")


def htmx_alert_error(user_id, text):
    htmx_alert_message(user_id, text, "error")


def htmx_alert_warning(user_id, text):
    htmx_alert_message(user_id, text, "warning")


def htmx_alert_info(user_id, text):
    htmx_alert_message(user_id, text, "info")

