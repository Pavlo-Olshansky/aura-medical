import json
import os

import structlog

logger = structlog.get_logger()

_KEYS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".vapid_keys.json")

_cached_keys: dict | None = None


def get_vapid_keys() -> dict:
    """Return {"private_key": str, "public_key": str}. Auto-generates on first call."""
    global _cached_keys
    if _cached_keys is not None:
        return _cached_keys

    if os.path.exists(_KEYS_FILE):
        with open(_KEYS_FILE) as f:
            _cached_keys = json.load(f)
        logger.info("VAPID keys loaded", path=_KEYS_FILE)
        return _cached_keys

    import base64
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from py_vapid import Vapid

    vapid = Vapid()
    vapid.generate_keys()

    private_pem = vapid.private_pem()
    pub_bytes = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    pub_b64 = base64.urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()

    _cached_keys = {
        "private_key": private_pem.decode() if isinstance(private_pem, bytes) else private_pem,
        "public_key": pub_b64,
    }

    with open(_KEYS_FILE, "w") as f:
        json.dump(_cached_keys, f, indent=2)

    logger.info("VAPID keys generated", path=_KEYS_FILE)
    return _cached_keys


def get_vapid_public_key() -> str:
    return get_vapid_keys()["public_key"]


def get_vapid_private_key() -> str:
    return get_vapid_keys()["private_key"]
