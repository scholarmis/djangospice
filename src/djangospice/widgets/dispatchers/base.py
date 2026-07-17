from abc import ABC, abstractmethod

from django.http import HttpRequest

from djangospice.widgets.base import BaseWidget


class Dispatcher(ABC):

    def __init__(self, widget: BaseWidget, request: HttpRequest):
        self.widget = widget
        self.request = request

    @abstractmethod
    def can_dispatch(self):
        pass

    @abstractmethod
    def dispatch(self):
        pass
    
