from django.db import models
from django.utils.translation import gettext_lazy as _

class IDType(models.TextChoices):
    NATIONAL_ID = 'NATIONAL_ID', _('National ID')
    PASSPORT = 'PASSPORT', _('International Passport')
    DRIVING_LICENSE = 'DRIVING_LICENSE', _('Driving License')
    RESIDENCE_PERMIT = 'RESIDENCE_PERMIT', _('Residence / Work Permit')
    TAX_IDENTIFICATION = 'TAX_IDENTIFICATION', _('Tax Identification Number')
    SOCIAL_SECURITY = 'SOCIAL_SECURITY', _('Social Security / Social Insurance')


class BloodType(models.TextChoices):
    A_POS = 'A+', 'A+'
    A_NEG = 'A-', 'A-'
    B_POS = 'B+', 'B+'
    B_NEG = 'B-', 'B-'
    O_POS = 'O+', 'O+'
    O_NEG = 'O-', 'O-'
    AB_POS = 'AB+', 'AB+'
    AB_NEG = 'AB-', 'AB-'



class Gender(models.TextChoices):
    MALE = 'MALE', _('Male')
    FEMALE = 'FEMALE', _('Female')
    NON_BINARY = 'NON_BINARY', _('Non-Binary')
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', _('Prefer not to say')
    OTHER = 'OTHER', _('Other')


class Sex(models.TextChoices):
    """Used strictly for legal, medical, or statutory regulatory reporting."""
    MALE = 'MALE', _('Male')
    FEMALE = 'FEMALE', _('Female')
    INTERSEX = 'INTERSEX', _('Intersex')


class MaritalStatus(models.TextChoices):
    SINGLE = 'SINGLE', _('Single')
    MARRIED = 'MARRIED', _('Married')
    DIVORCED = 'DIVORCED', _('Divorced')
    WIDOWED = 'WIDOWED', _('Widowed')
    SEPARATED = 'SEPARATED', _('Legally Separated')
    CIVIL_UNION = 'CIVIL_UNION', _('Civil Union / Domestic Partnership')


class Title(models.TextChoices):
    MR = 'MR', _('Mr.')
    MRS = 'MRS', _('Mrs.')
    MISS = 'MISS', _('Miss')
    MS = 'MS', _('Ms.')  
    DR = 'DR', _('Dr.')
    PROF = 'PROF', _('Prof.')
    SIR = 'SIR', _('Sir')
    REV = 'REV', _('Reverend')
    MX = 'MX', _('Mx.')      


class Relation(models.TextChoices):
    # Gendered Core
    FATHER = 'FATHER', _('Father')
    MOTHER = 'MOTHER', _('Mother')
    SON = 'SON', _('Son')
    DAUGHTER = 'DAUGHTER', _('Daughter')
    HUSBAND = 'HUSBAND', _('Husband')
    WIFE = 'WIFE', _('Wife')
    BROTHER = 'BROTHER', _('Brother')
    SISTER = 'SISTER', _('Sister')
    UNCLE = 'UNCLE', _('Uncle')
    AUNT = 'AUNT', _('Aunt')
    NEPHEW = 'NEPHEW', _('Nephew')
    NIECE = 'NIECE', _('Niece')
    GRANDFATHER = 'GRANDFATHER', _('Grandfather')
    GRANDMOTHER = 'GRANDMOTHER', _('Grandmother')
    
    SPOUSE = 'SPOUSE', _('Spouse')
    PARTNER = 'PARTNER', _('Domestic Partner')
    SIBLING = 'SIBLING', _('Sibling')
    CHILD = 'CHILD', _('Child')
    PARENT = 'PARENT', _('Parent')
    
    GUARDIAN = 'GUARDIAN', _('Legal Guardian')
    WARD = 'WARD', _('Ward')
    DEPENDENT = 'DEPENDENT', _('Other Dependent')
    EMERGENCY_CONTACT = 'EMERGENCY_CONTACT', _('Emergency Contact (No Relation)')