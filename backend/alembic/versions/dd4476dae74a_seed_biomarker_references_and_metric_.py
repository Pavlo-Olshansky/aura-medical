"""seed biomarker references and metric types

Revision ID: dd4476dae74a
Revises: bab58a7d6839
Create Date: 2026-04-01 13:23:35.079314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd4476dae74a'
down_revision: Union[str, Sequence[str], None] = 'bab58a7d6839'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


biomarker_reference = sa.table(
    "biomarker_reference",
    sa.column("name", sa.String),
    sa.column("abbreviation", sa.String),
    sa.column("unit", sa.String),
    sa.column("category", sa.String),
    sa.column("ref_min", sa.Numeric),
    sa.column("ref_max", sa.Numeric),
    sa.column("ref_min_male", sa.Numeric),
    sa.column("ref_max_male", sa.Numeric),
    sa.column("ref_min_female", sa.Numeric),
    sa.column("ref_max_female", sa.Numeric),
    sa.column("sort_order", sa.Integer),
)

metric_type = sa.table(
    "metric_type",
    sa.column("name", sa.String),
    sa.column("unit", sa.String),
    sa.column("has_secondary_value", sa.Boolean),
    sa.column("ref_min", sa.Numeric),
    sa.column("ref_max", sa.Numeric),
    sa.column("ref_min_secondary", sa.Numeric),
    sa.column("ref_max_secondary", sa.Numeric),
    sa.column("sort_order", sa.Integer),
)


def upgrade() -> None:
    # --- Biomarker References (28 rows) ---
    # All names in Ukrainian. Sex-specific ranges where clinically relevant.
    op.bulk_insert(biomarker_reference, [
        # CBC (Загальний аналіз крові)
        {"name": "Гемоглобін", "abbreviation": "Hb", "unit": "г/л", "category": "cbc",
         "ref_min": 120, "ref_max": 160, "ref_min_male": 130, "ref_max_male": 170,
         "ref_min_female": 120, "ref_max_female": 150, "sort_order": 1},
        {"name": "Еритроцити", "abbreviation": "RBC", "unit": "×10¹²/л", "category": "cbc",
         "ref_min": 3.5, "ref_max": 5.5, "ref_min_male": 4.0, "ref_max_male": 5.5,
         "ref_min_female": 3.5, "ref_max_female": 5.0, "sort_order": 2},
        {"name": "Лейкоцити", "abbreviation": "WBC", "unit": "×10⁹/л", "category": "cbc",
         "ref_min": 4.0, "ref_max": 9.0, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 3},
        {"name": "Тромбоцити", "abbreviation": "PLT", "unit": "×10⁹/л", "category": "cbc",
         "ref_min": 150, "ref_max": 400, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 4},
        {"name": "Гематокрит", "abbreviation": "Hct", "unit": "%", "category": "cbc",
         "ref_min": 35, "ref_max": 49, "ref_min_male": 39, "ref_max_male": 49,
         "ref_min_female": 35, "ref_max_female": 45, "sort_order": 5},
        {"name": "ШОЕ", "abbreviation": "ESR", "unit": "мм/год", "category": "cbc",
         "ref_min": 2, "ref_max": 15, "ref_min_male": 2, "ref_max_male": 10,
         "ref_min_female": 2, "ref_max_female": 15, "sort_order": 6},

        # Biochemistry (Біохімія)
        {"name": "Глюкоза", "abbreviation": "Glu", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": 3.9, "ref_max": 5.5, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 10},
        {"name": "Загальний холестерин", "abbreviation": "TC", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 5.2, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 11},
        {"name": "Холестерин ЛПВЩ", "abbreviation": "HDL", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": 1.0, "ref_max": 2.2, "ref_min_male": 1.0, "ref_max_male": 2.1,
         "ref_min_female": 1.2, "ref_max_female": 2.2, "sort_order": 12},
        {"name": "Холестерин ЛПНЩ", "abbreviation": "LDL", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 3.3, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 13},
        {"name": "Тригліцериди", "abbreviation": "TG", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 1.7, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 14},
        {"name": "Креатинін", "abbreviation": "Crea", "unit": "мкмоль/л", "category": "biochemistry",
         "ref_min": 44, "ref_max": 106, "ref_min_male": 62, "ref_max_male": 106,
         "ref_min_female": 44, "ref_max_female": 80, "sort_order": 15},
        {"name": "Сечовина", "abbreviation": "Urea", "unit": "ммоль/л", "category": "biochemistry",
         "ref_min": 2.5, "ref_max": 8.3, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 16},
        {"name": "АЛТ", "abbreviation": "ALT", "unit": "Од/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 41, "ref_min_male": None, "ref_max_male": 41,
         "ref_min_female": None, "ref_max_female": 33, "sort_order": 17},
        {"name": "АСТ", "abbreviation": "AST", "unit": "Од/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 40, "ref_min_male": None, "ref_max_male": 40,
         "ref_min_female": None, "ref_max_female": 32, "sort_order": 18},
        {"name": "Білірубін загальний", "abbreviation": "TBIL", "unit": "мкмоль/л", "category": "biochemistry",
         "ref_min": 3.4, "ref_max": 20.5, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 19},
        {"name": "Загальний білок", "abbreviation": "TP", "unit": "г/л", "category": "biochemistry",
         "ref_min": 64, "ref_max": 83, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 20},
        {"name": "Альбумін", "abbreviation": "ALB", "unit": "г/л", "category": "biochemistry",
         "ref_min": 35, "ref_max": 52, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 21},
        {"name": "Сечова кислота", "abbreviation": "UA", "unit": "мкмоль/л", "category": "biochemistry",
         "ref_min": 143, "ref_max": 416, "ref_min_male": 202, "ref_max_male": 416,
         "ref_min_female": 143, "ref_max_female": 339, "sort_order": 22},
        {"name": "Залізо сироваткове", "abbreviation": "Fe", "unit": "мкмоль/л", "category": "biochemistry",
         "ref_min": 9.0, "ref_max": 31.3, "ref_min_male": 11.6, "ref_max_male": 31.3,
         "ref_min_female": 9.0, "ref_max_female": 30.4, "sort_order": 23},
        {"name": "Феритин", "abbreviation": "Ferr", "unit": "нг/мл", "category": "biochemistry",
         "ref_min": 10, "ref_max": 250, "ref_min_male": 20, "ref_max_male": 250,
         "ref_min_female": 10, "ref_max_female": 120, "sort_order": 24},
        {"name": "С-реактивний білок", "abbreviation": "CRP", "unit": "мг/л", "category": "biochemistry",
         "ref_min": None, "ref_max": 5.0, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 25},
        {"name": "Глікований гемоглобін", "abbreviation": "HbA1c", "unit": "%", "category": "biochemistry",
         "ref_min": 4.0, "ref_max": 5.6, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 26},

        # Thyroid (Щитоподібна залоза)
        {"name": "ТТГ", "abbreviation": "TSH", "unit": "мМО/л", "category": "thyroid",
         "ref_min": 0.27, "ref_max": 4.2, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 30},
        {"name": "Вільний Т4", "abbreviation": "FT4", "unit": "пмоль/л", "category": "thyroid",
         "ref_min": 12.0, "ref_max": 22.0, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 31},
        {"name": "Вільний Т3", "abbreviation": "FT3", "unit": "пмоль/л", "category": "thyroid",
         "ref_min": 3.1, "ref_max": 6.8, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 32},

        # Vitamins (Вітаміни)
        {"name": "Вітамін D (25-OH)", "abbreviation": "25-OH-D", "unit": "нг/мл", "category": "vitamins",
         "ref_min": 30, "ref_max": 100, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 40},
        {"name": "Вітамін B12", "abbreviation": "B12", "unit": "пг/мл", "category": "vitamins",
         "ref_min": 197, "ref_max": 771, "ref_min_male": None, "ref_max_male": None,
         "ref_min_female": None, "ref_max_female": None, "sort_order": 41},
    ])

    # --- Metric Types (7 rows) ---
    op.bulk_insert(metric_type, [
        {"name": "Артеріальний тиск", "unit": "мм рт.ст.", "has_secondary_value": True,
         "ref_min": 90, "ref_max": 120, "ref_min_secondary": 60, "ref_max_secondary": 80, "sort_order": 1},
        {"name": "Пульс", "unit": "уд/хв", "has_secondary_value": False,
         "ref_min": 60, "ref_max": 100, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 2},
        {"name": "Температура тіла", "unit": "°C", "has_secondary_value": False,
         "ref_min": 35.5, "ref_max": 37.0, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 3},
        {"name": "Вага", "unit": "кг", "has_secondary_value": False,
         "ref_min": None, "ref_max": None, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 4},
        {"name": "Глюкоза крові", "unit": "ммоль/л", "has_secondary_value": False,
         "ref_min": 3.3, "ref_max": 5.5, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 5},
        {"name": "Сатурація кисню (SpO2)", "unit": "%", "has_secondary_value": False,
         "ref_min": 95, "ref_max": 100, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 6},
        {"name": "Частота дихання", "unit": "дих/хв", "has_secondary_value": False,
         "ref_min": 12, "ref_max": 20, "ref_min_secondary": None, "ref_max_secondary": None, "sort_order": 7},
    ])


def downgrade() -> None:
    op.execute("DELETE FROM metric_type")
    op.execute("DELETE FROM biomarker_reference")
