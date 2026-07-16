from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactChannel(models.TextChoices):
    PHONE = "PHONE", _("Phone")
    EMAIL = "EMAIL", _("Email")
    WEB = "WEB", _("Web / URL")
    FAX = "FAX", _("Fax")
    SOCIAL = "SOCIAL", _("Social Media")
    MESSAGING = "MESSAGING", _("Messaging Handle")
    
    
class ContactUsage(models.TextChoices):
    PRIMARY = "PRIMARY", _("Primary")
    WORK = "WORK", _("Work")
    PERSONAL = "PERSONAL", _("Personal")
    BILLING = "BILLING", _("Billing")
    EMERGENCY = "EMERGENCY", _("Emergency Contact")
    SUPPORT = "SUPPORT", _("Support / Helpdesk")
    MARKETING = "MARKETING", _("Marketing / Notifications")