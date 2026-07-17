from djangospice.widgets.dispatchers.base import Dispatcher


class MethodDispatcher(Dispatcher):

    def can_dispatch(self):
        return True

    def dispatch(self):

        handler = getattr(self.widget, self.request.method.lower())
        
        return handler(self.request)