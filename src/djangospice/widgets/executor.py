from django.http import HttpRequest
from djangospice.response.response import Response
from djangospice.widgets.base import BaseWidget
from djangospice.widgets.dispatchers.action import ActionDispatcher
from djangospice.widgets.dispatchers.method import MethodDispatcher
from djangospice.widgets.exceptions import DispatcherNotFound


class WidgetExecutor:
    
    dispatchers = (
        ActionDispatcher,
        MethodDispatcher,
    )

    def __init__(self, widget: BaseWidget, request: HttpRequest):
        self.widget = widget
        self.request = request

    def execute(self) -> Response: 
        self.widget.authorize()
        self.widget.initialize()
        self.widget.configure()
        return self.dispatch()
    
    def dispatch(self):
        for dispatcher in self.dispatchers:
            runtime = dispatcher(self.widget,self.request)
            if runtime.can_dispatch():
                return runtime.dispatch()     
        raise DispatcherNotFound()