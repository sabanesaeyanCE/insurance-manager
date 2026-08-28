from enum import StrEnum


class InsuranceType(StrEnum):
    

    THIRD_PARTY = "ثالث"
    BODY = "بدنه"
    FIRE = "آتش‌سوزی"
    LIFE = "عمر"
    HEALTH = "درمان"
    LIABILITY = "مسئولیت"
    ACCIDENT = "حوادث"

    def get_label(self, lang: str = "fa") -> str:
       
        labels = {
            InsuranceType.THIRD_PARTY: {
                "fa": "ثالث",
                "en": "Third-Party Auto",
            },
            InsuranceType.BODY: {
                "fa": "بدنه",
                "en": "Comprehensive Auto",
            },
            InsuranceType.FIRE: {
                "fa": "آتش‌سوزی",
                "en": "Fire Insurance",
            },
            InsuranceType.LIFE: {
                "fa": "عمر",
                "en": "Life Insurance",
            },
            InsuranceType.HEALTH: {
                "fa":"درمان",
                "en": "Health",
            },
            InsuranceType.LIABILITY: {
                "fa": "مسئولیت",
                "en": "General Liability",
            },
            InsuranceType.ACCIDENT: {
                "fa": "حوادث",
                "en": "Personal Accident",
            },
        }
       
        return labels[self].get(lang, labels[self]["fa"])