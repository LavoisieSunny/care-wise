from cryptography.fernet import Fernet
from app.core.config import settings

_fernet = Fernet(settings.DATA_ENCRYPTION_KEY.encode())


def encrypt_text(plaintext: str) -> str:
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_text(ciphertext: str) -> str:
    return _fernet.decrypt(ciphertext.encode()).decode()
