from django.db import models
from django.utils.translation import gettext_lazy as _

class Weekday(models.TextChoices):
    MONDAY = "Monday", _("Monday")
    TUESDAY = "Tuesday", _("Tuesday")
    WEDNESDAY = "Wednesday", _("Wednesday")
    THURSDAY = "Thursday", _("Thursday")
    FRIDAY = "Friday", _("Friday")
    SATURDAY = "Saturday", _("Saturday")
    SUNDAY = "Sunday", _("Sunday")


class Month(models.TextChoices):
    JANUARY = "January", _("January")
    FEBRUARY = "February", _("February")
    MARCH = "March", _("March")
    APRIL = "April", _("April")
    MAY = "May", _("May")
    JUNE = "June", _("June")
    JULY = "July", _("July")
    AUGUST = "August", _("August")
    SEPTEMBER = "September", _("September")
    OCTOBER = "October", _("October")
    NOVEMBER = "November", _("November")
    DECEMBER = "December", _("December")


class Recurrence(models.TextChoices):
    ONCE = "Once", _("Once")
    HOURLY = "Hourly", _("Hourly")
    DAILY = "Daily", _("Daily")
    WEEKLY = "Weekly", _("Weekly")
    MONTHLY = "Monthly", _("Monthly")
    QUARTERLY = "Quarterly", _("Quarterly")
    YEARLY = "Yearly", _("Yearly")  # Fixed capitalization inconsistency here

    @classmethod
    def is_finite(cls, value):
        return value == cls.ONCE

    @classmethod
    def is_calendar_based(cls, value):
        return value in {
            cls.DAILY,
            cls.WEEKLY,
            cls.MONTHLY,
            cls.QUARTERLY,
            cls.YEARLY,
        }