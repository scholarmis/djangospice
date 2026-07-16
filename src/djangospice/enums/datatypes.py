from django.db import models
from django.utils.translation import gettext_lazy as _

class DataType(models.TextChoices):
    # --- Primitives & Text ---
    STRING = "string", _("String (Short Text)")
    TEXT = "text", _("Text (Long Text)")
    INTEGER = "integer", _("Integer")
    BIG_INTEGER = "big_integer", _("Big Integer")
    FLOAT = "float", _("Float (Floating-Point)")
    DECIMAL = "decimal", _("Decimal (Fixed-Point/Currency)")
    BOOLEAN = "boolean", _("Boolean")
    
    # --- Date & Time ---
    DATE = "date", _("Date")
    DATETIME = "datetime", _("DateTime")
    TIME = "time", _("Time")
    DURATION = "duration", _("Duration")
    
    # --- Complex & Network ---
    JSON = "json", _("JSON")
    UUID = "uuid", _("UUID")
    EMAIL = "email", _("Email")
    URL = "url", _("URL")
    IP_ADDRESS = "ip_address", _("IP Address")
    
    # --- Files & Media ---
    FILE = "file", _("File Upload")
    IMAGE = "image", _("Image Upload")