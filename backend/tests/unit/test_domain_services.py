import bcrypt

from app.domain.services import PasswordService


def test_verify_bcrypt_correct():
    pw_hash = bcrypt.hashpw(b"mypassword", bcrypt.gensalt(rounds=4)).decode()
    assert PasswordService.verify("mypassword", pw_hash) is True


def test_verify_bcrypt_wrong():
    pw_hash = bcrypt.hashpw(b"mypassword", bcrypt.gensalt(rounds=4)).decode()
    assert PasswordService.verify("wrongpassword", pw_hash) is False


def test_verify_unknown_hash_format():
    assert PasswordService.verify("test", "unknown_hash_format") is False


def test_verify_empty_password():
    pw_hash = bcrypt.hashpw(b"", bcrypt.gensalt(rounds=4)).decode()
    assert PasswordService.verify("", pw_hash) is True
    assert PasswordService.verify("notempty", pw_hash) is False
