# Standard Library
import base64

# Django
from django.conf import settings

# Libraries
from cryptography.fernet import Fernet
import hashlib


class FernetCrypto:
    clave_aes = base64.urlsafe_b64encode(settings.SECRET_KEY[0:32].encode())
    fernet = Fernet(clave_aes)

    @classmethod
    def encrypt(cls, value: str) -> str:
        return cls.fernet.encrypt(value.encode()).decode()

    @classmethod
    def decrypt(cls, value: str) -> str:
        return cls.fernet.decrypt(value.encode()).decode()

    @classmethod
    def verify_signature(cls, value: str) -> bool:
        try:
            cls.decrypt(value)
            return True
        except (Exception,):
            return False


def md5(text: str) -> str:
    try:
        _md5 = hashlib.md5()
        _md5.update(text.encode("utf-8"))
        hash_md5 = _md5.hexdigest()
        return hash_md5
    except Exception as e:
        return str(e)
