from enum import Enum


class CompanyType(str, Enum):
    MEDICAL = "Медицинские услуги"
    NON_MEDICAL = "Общие услуги"
