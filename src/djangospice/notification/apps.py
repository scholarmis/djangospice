from djangospice.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "djangospice.notification"
    namespace = "notification"
    
    
namespace = NotificationConfig.namespace