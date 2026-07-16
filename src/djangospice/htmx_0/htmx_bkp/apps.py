from django.apps import AppConfig


class HtmxConfig(AppConfig):
    name = "djarf.htmx"
    label = "htmx"

    def ready(self):
        pass
    

app_name = HtmxConfig.label

