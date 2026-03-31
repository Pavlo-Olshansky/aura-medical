import pytest

from app.domain.exceptions import DomainError
from app.domain.value_objects import BODY_REGION_KEYS, BodyRegion


def test_validate_valid_region():
    for key in BODY_REGION_KEYS:
        BodyRegion.validate(key)  # should not raise


def test_validate_invalid_region():
    with pytest.raises(DomainError, match="Invalid body region"):
        BodyRegion.validate("invalid_region")


def test_validate_empty_string():
    with pytest.raises(DomainError):
        BodyRegion.validate("")
