import jwt
import re
import random
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
from users.models import User
from users.services.auth_service import AuthService
from users.services.jwt_service import JWTService
from unittest.mock import patch, MagicMock


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Juan Perez",
            email="juan@example.com",
            phone="1234567890",
            address="Calle 123"
        )
        self.user.set_password("Password123!")
        self.user.save()

    def test_password_is_hashed(self):
        """Verifica que la contraseña se encripte correctamente"""
        self.assertNotEqual(self.user.password, "Password123!")
        self.assertTrue(self.user.check_password("Password123!"))

    def test_check_password_incorrect(self):
        """Verifica que falle con contraseña incorrecta"""
        self.assertFalse(self.user.check_password("WrongPass"))

    def test_check_password_empty(self):
        """Verifica manejo de contraseñas vacías"""
        self.assertFalse(self.user.check_password(""))
        self.assertFalse(self.user.check_password(None))

    def test_set_password_validation(self):
        """Verifica que no se puede setear contraseña vacía"""
        with self.assertRaises(ValueError):
            self.user.set_password("")


class AuthServiceTest(TestCase):
    def setUp(self):
        self.valid_email = "test@example.com"
        self.valid_password = "Password123!"
        self.user = User.objects.create(
            name="Tester",
            email=self.valid_email,
            phone="1234567890",
            address="Av Siempre Viva"
        )
        self.user.set_password(self.valid_password)
        self.user.save()

    def test_validate_email_valid(self):
        """Emails válidos"""
        valid_emails = [
            "usuario@dominio.com",
            "test+tag@example.co.uk",
            "user.name@sub.domain.com"
        ]
        for email in valid_emails:
            self.assertTrue(AuthService.validate_email(email))

    def test_validate_email_invalid(self):
        """Emails inválidos"""
        invalid_emails = [
            "usuario@dominio",
            "@dominio.com",
            "usuario@",
            "usuario",
            ""
        ]
        for email in invalid_emails:
            self.assertFalse(AuthService.validate_email(email))

    def test_validate_password_strength(self):
        """Contraseña válida con todos los requisitos"""
        valid, msg = AuthService.validate_password("Password123!")
        self.assertTrue(valid)
        self.assertEqual(msg, "OK")

    def test_validate_password_too_short(self):
        """Contraseña muy corta"""
        valid, msg = AuthService.validate_password("Pass1!")
        self.assertFalse(valid)
        self.assertIn("al menos", msg.lower())

    def test_validate_password_no_uppercase(self):
        """Contraseña sin mayúsculas"""
        valid, msg = AuthService.validate_password("password123!")
        self.assertFalse(valid)
        self.assertIn("mayúscula", msg.lower())

    def test_validate_password_no_lowercase(self):
        """Contraseña sin minúsculas"""
        valid, msg = AuthService.validate_password("PASSWORD123!")
        self.assertFalse(valid)
        self.assertIn("minúscula", msg.lower())

    def test_validate_password_no_digit(self):
        """Contraseña sin números"""
        valid, msg = AuthService.validate_password("Password!")
        self.assertFalse(valid)
        self.assertIn("número", msg.lower())

    def test_validate_password_no_special(self):
        """Contraseña sin caracteres especiales"""
        valid, msg = AuthService.validate_password("Password123")
        self.assertFalse(valid)
        self.assertIn("especial", msg.lower())

    def test_create_user_success(self):
        """Creación exitosa de usuario"""
        user, msg = AuthService.create_user(
            "Nuevo", "nuevo@ejemplo.com", "1112223333", "Password123!", "Calle Falsa"
        )
        self.assertIsNotNone(user)
        self.assertEqual(msg, "Usuario creado exitosamente")
        # Verificar que el email se guardó en minúsculas
        self.assertEqual(user.email, "nuevo@ejemplo.com")

    def test_create_user_existing_email(self):
        """No permite email duplicado"""
        user, msg = AuthService.create_user(
            "Repetido", self.valid_email, "1112223333", "Password123!", "Calle"
        )
        self.assertIsNone(user)
        self.assertEqual(msg, "El email ya está registrado")

    def test_create_user_invalid_email(self):
        """No permite email inválido"""
        user, msg = AuthService.create_user(
            "Test", "invalid-email", "1112223333", "Password123!", "Dir"
        )
        self.assertIsNone(user)
        self.assertEqual(msg, "Email inválido")

    def test_login_success(self):
        """Login exitoso genera tokens"""
        result, msg = AuthService.login(self.valid_email, self.valid_password)
        self.assertIsNotNone(result)
        self.assertIn("access", result)
        self.assertIn("refresh", result)
        self.assertIn("name", result)
        self.assertIn("email", result)
        self.assertEqual(msg, "Login exitoso")
        
        # Verificar que los tokens se guardaron en la BD
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.token)
        self.assertIsNotNone(self.user.refresh_token)

    def test_login_wrong_password(self):
        """Login falla con contraseña incorrecta"""
        result, msg = AuthService.login(self.valid_email, "WrongPass")
        self.assertIsNone(result)
        self.assertIn("incorrecta", msg.lower())

    def test_login_nonexistent_user(self):
        """Login falla con usuario inexistente"""
        result, msg = AuthService.login("noexiste@example.com", "Password123!")
        self.assertIsNone(result)
        self.assertIn("no encontrado", msg.lower())

    def test_verify_token_valid(self):
        """Verificación de token válido"""
        tokens = JWTService.generate_tokens(self.user)
        user, msg = AuthService.verify_token(tokens['access'])
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.valid_email)

    def test_verify_token_invalid(self):
        """Verificación de token inválido"""
        user, msg = AuthService.verify_token("token_invalido")
        self.assertIsNone(user)

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_request_password_reset_success(self, mock_send_email):
        """Solicitud de reseteo de contraseña exitosa"""
        mock_send_email.return_value = True
        
        success, msg = AuthService.request_password_reset(self.valid_email)
        
        self.assertTrue(success)
        self.assertIn("exitosamente", msg.lower())
        
        # Verificar que se generó el código
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_code)
        self.assertIsNotNone(self.user.reset_code_expires)
        self.assertFalse(self.user.reset_code_used)
        self.assertEqual(len(self.user.reset_code), 6)

    def test_request_password_reset_nonexistent_user(self):
        """Reseteo falla con usuario inexistente"""
        success, msg = AuthService.request_password_reset("noexiste@example.com")
        self.assertFalse(success)

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_with_token_success(self, mock_send_email):
        """Reseteo de contraseña exitoso con código válido"""
        mock_send_email.return_value = True
        
        # Solicitar código
        AuthService.request_password_reset(self.valid_email)
        self.user.refresh_from_db()
        code = self.user.reset_code
        
        # Resetear contraseña
        success, msg = AuthService.reset_password_with_token(
            self.valid_email, code, "NewPassword123!", "NewPassword123!"
        )
        
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))
        self.assertTrue(self.user.reset_code_used)

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_invalid_code(self, mock_send_email):
        """Reseteo falla con código inválido"""
        mock_send_email.return_value = True
        AuthService.request_password_reset(self.valid_email)
        
        success, msg = AuthService.reset_password_with_token(
            self.valid_email, "000000", "NewPassword123!", "NewPassword123!"
        )
        
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_code_already_used(self, mock_send_email):
        """Reseteo falla si el código ya fue usado"""
        mock_send_email.return_value = True
        AuthService.request_password_reset(self.valid_email)
        self.user.refresh_from_db()
        code = self.user.reset_code
        
        # Usar el código una vez
        AuthService.reset_password_with_token(
            self.valid_email, code, "NewPassword123!", "NewPassword123!"
        )
        
        # Intentar usar de nuevo
        success, msg = AuthService.reset_password_with_token(
            self.valid_email, code, "AnotherPass123!", "AnotherPass123!"
        )
        
        self.assertFalse(success)
        self.assertIn("usado", msg.lower())

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_expired_code(self, mock_send_email):
        """Reseteo falla con código expirado"""
        mock_send_email.return_value = True
        AuthService.request_password_reset(self.valid_email)
        self.user.refresh_from_db()
        code = self.user.reset_code
        
        # Expirar el código
        self.user.reset_code_expires = timezone.now() - timedelta(minutes=1)
        self.user.save()
        
        success, msg = AuthService.reset_password_with_token(
            self.valid_email, code, "NewPassword123!", "NewPassword123!"
        )
        
        self.assertFalse(success)
        self.assertIn("expirado", msg.lower())

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_mismatch(self, mock_send_email):
        """Reseteo falla si las contraseñas no coinciden"""
        mock_send_email.return_value = True
        AuthService.request_password_reset(self.valid_email)
        self.user.refresh_from_db()
        
        success, msg = AuthService.reset_password_with_token(
            self.valid_email, self.user.reset_code, "Password123!", "Different123!"
        )
        
        self.assertFalse(success)
        self.assertIn("no coinciden", msg.lower())

    def test_logout_clears_tokens(self):
        """Logout limpia todos los tokens"""
        self.user.token = "abc"
        self.user.refresh_token = "xyz"
        self.user.token_expires = timezone.now()
        self.user.refresh_token_expires = timezone.now()
        self.user.save()
        
        success, msg = AuthService.logout(self.user)
        
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.token)
        self.assertIsNone(self.user.refresh_token)
        self.assertIsNone(self.user.token_expires)
        self.assertIsNone(self.user.refresh_token_expires)


class JWTServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="JWTUser",
            email="jwt@example.com",
            phone="0000000000",
            address="Dir"
        )
        self.user.set_password("Password123!")
        self.user.save()

    def test_generate_tokens_structure(self):
        """Tokens generados tienen la estructura correcta"""
        tokens = JWTService.generate_tokens(self.user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIn('access_expires', tokens)
        self.assertIn('refresh_expires', tokens)
        
        # Verificar que son strings no vacíos
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
        self.assertGreater(len(tokens['access']), 0)

    def test_generate_and_verify_access_token(self):
        """Token de acceso se genera y verifica correctamente"""
        tokens = JWTService.generate_tokens(self.user)
        payload, msg = JWTService.verify_access_token(tokens["access"])
        
        self.assertIsNotNone(payload)
        self.assertIsNone(msg)
        self.assertEqual(payload["email"], self.user.email)
        self.assertEqual(payload["token_type"], "access")
        self.assertIn("jti", payload)

    def test_generate_and_verify_refresh_token(self):
        """Token de refresco se genera y verifica correctamente"""
        tokens = JWTService.generate_tokens(self.user)
        payload, msg = JWTService.verify_refresh_token(tokens["refresh"])
        
        self.assertIsNotNone(payload)
        self.assertIsNone(msg)
        self.assertEqual(payload["email"], self.user.email)
        self.assertEqual(payload["token_type"], "refresh")

    def test_verify_wrong_token_type(self):
        """No se puede verificar access token como refresh y viceversa"""
        tokens = JWTService.generate_tokens(self.user)
        
        # Intentar verificar access como refresh
        payload, msg = JWTService.verify_refresh_token(tokens["access"])
        self.assertIsNone(payload)
        self.assertIn("inválido", msg.lower())
        
        # Intentar verificar refresh como access
        payload, msg = JWTService.verify_access_token(tokens["refresh"])
        self.assertIsNone(payload)
        self.assertIn("inválido", msg.lower())

    def test_invalid_token(self):
        """Token inválido retorna None"""
        payload, msg = JWTService.verify_access_token("token_invalido")
        self.assertIsNone(payload)
        self.assertIsNotNone(msg)
        self.assertIn("inválido", msg.lower())

    def test_expired_token(self):
        """Token expirado es detectado"""
        # Crear token que expire inmediatamente
        import jwt
        from datetime import datetime, timezone
        
        payload = {
            'email': self.user.email,
            'token_type': 'access',
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),
            'iat': datetime.now(timezone.utc),
            'jti': 'test-jti'
        }
        
        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        result, msg = JWTService.verify_access_token(expired_token)
        self.assertIsNone(result)
        self.assertIn("expirado", msg.lower())


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "user@test.com"
        self.password = "Password123!"
        self.user = User.objects.create(
            name="UserTest",
            email=self.email,
            phone="9999999999",
            address="Dir 1"
        )
        self.user.set_password(self.password)
        self.user.save()

    def test_register_user_success(self):
        """Registro exitoso de usuario"""
        url = reverse("register")
        data = {
            "name": "Nuevo",
            "email": "nuevo@test.com",
            "phone": "8888888888",
            "password": "Password123!",
            "address": "Dir 2"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["status"], 201)
        self.assertIn("message", response.data)

    def test_register_missing_email(self):
        """Registro falla sin email"""
        url = reverse("register")
        data = {"name": "Test", "password": "Password123!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_missing_password(self):
        """Registro falla sin contraseña"""
        url = reverse("register")
        data = {"name": "Test", "email": "test@test.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_email(self):
        """Registro falla con email duplicado"""
        url = reverse("register")
        data = {
            "name": "Duplicate",
            "email": self.email,
            "phone": "7777777777",
            "password": "Password123!",
            "address": "Dir"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_login_success(self):
        """Login exitoso retorna tokens"""
        url = reverse("login")
        data = {"email": self.email, "password": self.password}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], self.email)

    def test_login_invalid_credentials(self):
        """Login falla con credenciales inválidas"""
        url = reverse("login")
        data = {"email": self.email, "password": "Wrong"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_login_missing_fields(self):
        """Login falla sin campos requeridos"""
        url = reverse("login")
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_get_user_profile_authenticated(self):
        """Obtener perfil con autenticación"""
        # DEBUG: Verificar que el usuario existe
        tokens = JWTService.generate_tokens(self.user)
        self.user.token = tokens["access"]
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)


    def test_get_user_profile_unauthenticated(self):
        """Obtener perfil sin autenticación falla"""
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_logout_authenticated(self):
        """Logout exitoso"""
        tokens = JWTService.generate_tokens(self.user)
        self.user.token = tokens["access"]
        self.user.save()
        
        self.client.force_authenticate(user=self.user)
        url = reverse("logout")
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que los tokens fueron eliminados
        self.user.refresh_from_db()
        self.assertIsNone(self.user.token)

    def test_logout_unauthenticated(self):
        """Logout sin autenticación falla"""
        url = reverse("logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_send_code_password_reset(self, mock_send_email):
        """Envío de código de reseteo"""
        mock_send_email.return_value = True
        
        url = reverse("send_code_password_reset")
        data = {"email": self.email}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    @patch('comunications.services.email_service.EmailService.send_email')
    def test_reset_password_with_code(self, mock_send_email):
        """Reseteo de contraseña con código"""
        mock_send_email.return_value = True
        
        # Primero solicitar código
        send_url = reverse("send_code_password_reset")
        self.client.post(send_url, {"email": self.email})
        
        self.user.refresh_from_db()
        code = self.user.reset_code
        
        # Resetear contraseña
        reset_url = reverse("reset_password_code")
        data = {
            "email": self.email,
            "code": code,
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = self.client.post(reset_url, data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la contraseña cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))