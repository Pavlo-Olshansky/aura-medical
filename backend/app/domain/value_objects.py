from app.domain.exceptions import DomainError

BODY_REGION_KEYS = (
    "head_cranium", "head_face", "eyes", "ears", "mouth_teeth",
    "neck_throat", "chest", "abdomen_upper", "abdomen_lower", "pelvis",
    "back_upper", "back_lower",
    "shoulder_left", "shoulder_right",
    "arm_left", "arm_right", "hand_left", "hand_right",
    "leg_left", "leg_right", "foot_left", "foot_right",
    "whole_body",
)


class BodyRegion:
    @staticmethod
    def validate(value: str) -> None:
        if value not in BODY_REGION_KEYS:
            raise DomainError(f"Invalid body region: {value}")


BODY_REGION_LABELS: dict[str, str] = {
    "head_cranium": "Голова (черепна частина)",
    "head_face": "Обличчя",
    "eyes": "Очі",
    "ears": "Вуха",
    "mouth_teeth": "Рот і зуби",
    "neck_throat": "Шия / горло",
    "chest": "Грудна клітка",
    "abdomen_upper": "Верхня частина живота",
    "abdomen_lower": "Нижня частина живота",
    "pelvis": "Таз",
    "back_upper": "Верхня частина спини",
    "back_lower": "Нижня частина спини",
    "shoulder_left": "Ліве плече",
    "shoulder_right": "Праве плече",
    "arm_left": "Ліва рука",
    "arm_right": "Права рука",
    "hand_left": "Ліва кисть",
    "hand_right": "Права кисть",
    "leg_left": "Ліва нога",
    "leg_right": "Права нога",
    "foot_left": "Ліва стопа",
    "foot_right": "Права стопа",
    "whole_body": "Все тіло",
}

SPECIALTY_REGION_MAP: dict[str, list[str]] = {
    "Кардіолог": ["chest"],
    "Офтальмолог": ["eyes"],
    "Стоматолог": ["mouth_teeth"],
    "Отоларинголог": ["ears", "neck_throat", "head_face"],
    "ЛОР": ["ears", "neck_throat", "head_face"],
    "Гастроентеролог": ["abdomen_upper", "abdomen_lower"],
    "Невролог": ["head_cranium", "neck_throat", "back_upper", "back_lower"],
    "Пульмонолог": ["chest", "back_upper"],
    "Ендокринолог": ["neck_throat"],
    "Уролог": ["abdomen_lower", "pelvis"],
    "Гінеколог": ["pelvis", "abdomen_lower"],
    "Мамолог": ["chest"],
    "Нефролог": ["back_lower", "abdomen_lower"],
    "Психіатр": ["head_cranium"],
}
