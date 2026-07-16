from django.db import models
from django.utils.translation import gettext_lazy as _

class ProcessStatus(models.TextChoices):
    PENDING = "Pending", _("Pending")
    PROCESSING = "Processing", _("Processing")
    READY = "Ready", _("Ready")
    ERROR = "Error", _("Error")


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    RUNNING = "RUNNING", _("Running")
    SUCCESS = "SUCCESS", _("Success")
    FAILURE = "FAILURE", _("Failure")
    ERROR = "ERROR", _("Error")
    CANCELLED = "CANCELLED", _("Cancelled")
    

class Status(models.TextChoices):
    ACTIVE = 'ACTIVE', _('Active')
    INACTIVE = 'INACTIVE', _('Inactive')
    PENDING = 'PENDING', _('Pending / Onboarding')
    SUSPENDED = 'SUSPENDED', _('Suspended')
    TERMINATED = 'TERMINATED', _('Terminated / Archived')

