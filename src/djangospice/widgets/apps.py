from djangospice.apps import AppConfig


class WidgetsConfig(AppConfig):
    name = "djangospice.widgets"
    namespace = "widgets"
    
    
namespace = WidgetsConfig.namespace