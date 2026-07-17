from djangospice.widgets.dispatchers.base import Dispatcher


class ActionDispatcher(Dispatcher):

    parameter = "action"

    def can_dispatch(self):
        return self.parameter in self.request.POST or self.parameter in self.request.GET

    def dispatch(self):
        action_name =  self.request.POST.get("action") or self.request.GET.get("action")
        action = self.widget.get_action(action_name)
        action.authorize(self.widget)
        action.before_execute(self.widget)
        response = action.execute(self.widget, self.request)
        action.after_execute(response)
        return response
         