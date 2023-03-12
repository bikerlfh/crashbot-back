import base64
from cryptography.fernet import Fernet
from django.conf import settings


class FernetCrypto:
    clave_aes = base64.urlsafe_b64encode(settings.SECRET_KEY[0:32].encode())
    fernet = Fernet(clave_aes)

    @classmethod
    def encrypt(cls, value: str) -> str:
        return cls.fernet.encrypt(value.encode()).decode()

    @classmethod
    def decrypt(cls, value: str) -> str:
        return cls.fernet.decrypt(value.encode()).decode()
