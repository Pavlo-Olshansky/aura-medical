import base64
import hashlib

import bcrypt


class PasswordService:
    @staticmethod
    def verify(plain_password: str, stored_hash: str) -> bool:
        if stored_hash.startswith("pbkdf2_sha256$"):
            parts = stored_hash.split("$")
            if len(parts) != 4:
                return False
            iterations = int(parts[1])
            salt = parts[2]
            expected_hash = parts[3]
            dk = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode(), salt.encode(), iterations
            )
            return base64.b64encode(dk).decode() == expected_hash
        elif stored_hash.startswith("$2"):
            return bcrypt.checkpw(plain_password.encode(), stored_hash.encode())
        return False
