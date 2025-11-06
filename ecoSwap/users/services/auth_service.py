from ..models import Users, ImagesUsers
from passlib.hash import pbkdf2_sha256


class AuthService:

    @classmethod
    def validate_password(cls, password: str) -> bool:
        """Valida la contraseña"""
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        return True