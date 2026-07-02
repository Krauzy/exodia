import pytest
from pydantic import ValidationError

from app.schemas.sre import SreCheckRequest
from app.schemas.targets import TargetCreate


def test_web_target_requires_http_or_https() -> None:
    with pytest.raises(ValidationError):
        TargetCreate(
            name="bad target",
            target_type="web",
            value="ftp://example.test",
            authorization_scope="owned lab target",
        )


def test_host_target_accepts_ip() -> None:
    target = TargetCreate(
        name="lab host",
        target_type="host",
        value="10.10.0.5",
        authorization_scope="owned lab host for local validation",
    )

    assert target.value == "10.10.0.5"


def test_sre_check_requires_http_url() -> None:
    with pytest.raises(ValidationError):
        SreCheckRequest(
            url="ftp://example.test",
            authorization_confirmed=True,
        )


def test_sre_check_requires_authorization() -> None:
    with pytest.raises(ValidationError):
        SreCheckRequest(
            url="https://example.test",
            authorization_confirmed=False,
        )
