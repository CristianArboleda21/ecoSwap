import json
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from users.models import User
from publications.models import Publications
from exchanges.models import Exchange
from exchanges.services.exchange_service import ExchangeService
from users.services.jwt_service import JWTService


class ExchangeModelTest(TestCase):
    """Tests para el modelo Exchange"""
    
    def setUp(self):
        # Crear usuarios
        self.user1 = User.objects.create(
            name="Usuario1",
            email="user1@test.com",
            phone="1111111111",
            address="Dir 1"
        )
        self.user1.set_password("Password123!")
        self.user1.save()
        
        self.user2 = User.objects.create(
            name="Usuario2",
            email="user2@test.com",
            phone="2222222222",
            address="Dir 2"
        )
        self.user2.set_password("Password123!")
        self.user2.save()
        
        # Crear publicaciones
        self.pub1 = Publications.objects.create(
            user=self.user1,
            title="Libro de Python",
            description="Libro excelente"
        )
        
        self.pub2 = Publications.objects.create(
            user=self.user2,
            title="Laptop Dell",
            description="Laptop en buen estado"
        )
    
    def test_create_exchange(self):
        """Crear un intercambio básico"""
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        self.assertEqual(exchange.requested_item, self.pub1)
        self.assertEqual(exchange.offered_item, self.pub2)
        self.assertEqual(exchange.status, Exchange.Status.PENDING)
        self.assertIsNotNone(exchange.created_at)
    
    def test_exchange_status_choices(self):
        """Verificar que todos los estados están disponibles"""
        statuses = [
            Exchange.Status.PENDING,
            Exchange.Status.IN_PROCESS,
            Exchange.Status.ACCEPTED,
            Exchange.Status.REJECTED,
            Exchange.Status.CANCELLED
        ]
        
        for status_choice in statuses:
            exchange = Exchange.objects.create(
                requested_item=self.pub1,
                offered_item=self.pub2,
                status=status_choice
            )
            self.assertEqual(exchange.status, status_choice)
            exchange.delete()
    
    def test_exchange_related_names(self):
        """Verificar las relaciones inversas"""
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        # Verificar exchange_requests
        self.assertIn(exchange, self.pub1.exchange_requests.all())
        
        # Verificar exchange_offers
        self.assertIn(exchange, self.pub2.exchange_offers.all())


class ExchangeServiceTest(TestCase):
    """Tests para ExchangeService"""
    
    def setUp(self):
        # Crear usuarios
        self.user1 = User.objects.create(
            name="Usuario1",
            email="user1@test.com",
            phone="1111111111",
            address="Dir 1"
        )
        self.user1.set_password("Password123!")
        self.user1.save()
        
        self.user2 = User.objects.create(
            name="Usuario2",
            email="user2@test.com",
            phone="2222222222",
            address="Dir 2"
        )
        self.user2.set_password("Password123!")
        self.user2.save()
        
        # Crear publicaciones
        self.pub1 = Publications.objects.create(
            user=self.user1,
            title="Libro de Python",
            description="Libro excelente",
        )
        
        self.pub2 = Publications.objects.create(
            user=self.user2,
            title="Laptop Dell",
            description="Laptop en buen estado",
        )
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_create_exchange_success(self, mock_send_email):
        """Crear intercambio exitosamente"""
        mock_send_email.return_value = True
        
        success, message = ExchangeService.create_exchange(
            request_item=self.pub1.id,
            offered_item=self.pub2.id,
            status_exchange=Exchange.Status.PENDING
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Oferta de intercambio enviada.")
        
        # Verificar que se creó en la BD
        exchange = Exchange.objects.filter(
            requested_item=self.pub1,
            offered_item=self.pub2
        ).first()
        self.assertIsNotNone(exchange)
        self.assertEqual(exchange.status, Exchange.Status.PENDING)
        
        # Verificar que se envió email
        mock_send_email.assert_called_once()
    
    def test_create_exchange_invalid_publication(self):
        """Crear intercambio con publicación inexistente"""
        success, message = ExchangeService.create_exchange(
            request_item=99999,  # ID inexistente
            offered_item=self.pub2.id,
            status_exchange=Exchange.Status.PENDING
        )
        
        self.assertFalse(success)
        self.assertIn("no existe", message.lower())
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_respond_exchange_success(self, mock_send_email):
        """Responder a intercambio exitosamente"""
        mock_send_email.return_value = True
        
        # Crear intercambio
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        # Responder
        success, message = ExchangeService.respond_exchange(
            exchange_id=exchange.id,
            response_status=Exchange.Status.ACCEPTED
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Respuesta a la oferta de intercambio fue enviada.")
        
        # Verificar actualización
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, Exchange.Status.ACCEPTED)
        self.assertIsNotNone(exchange.updated_at)
    
    def test_respond_exchange_not_found(self):
        """Responder a intercambio inexistente"""
        success, message = ExchangeService.respond_exchange(
            exchange_id=99999,
            response_status=Exchange.Status.ACCEPTED
        )
        
        self.assertFalse(success)
        self.assertIn("no existe", message.lower())
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_success(self, mock_send_email):
        """Cancelar intercambio exitosamente"""
        mock_send_email.return_value = True
        
        # Crear intercambio aceptado
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        exchange.updated_at = timezone.now()
        exchange.save()
        
        # Cancelar
        success, message = ExchangeService.cancel_exchange(
            exchange_id=exchange.id,
            email_user=self.user1.email,
            reason="Ya no me interesa"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Oferta de intercambio cancelada.")
        
        # Verificar estado
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, Exchange.Status.CANCELLED)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_not_accepted(self, mock_send_email):
        """No se puede cancelar si no está aceptado"""
        mock_send_email.return_value = True
        
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        success, message = ExchangeService.cancel_exchange(
            exchange_id=exchange.id,
            email_user=self.user1.email,
            reason="Test"
        )
        
        self.assertFalse(success)
        self.assertIn("aceptada", message.lower())
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_no_permission(self, mock_send_email):
        """Usuario sin permiso no puede cancelar"""
        mock_send_email.return_value = True
        
        # Crear un tercer usuario
        user3 = User.objects.create(
            name="Usuario3",
            email="user3@test.com",
            phone="3333333333",
            address="Dir 3"
        )
        
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        
        success, message = ExchangeService.cancel_exchange(
            exchange_id=exchange.id,
            email_user=user3.email,
            reason="Test"
        )
        
        self.assertFalse(success)
        self.assertIn("permiso", message.lower())
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_expired(self, mock_send_email):
        """No se puede cancelar después de 5 días"""
        mock_send_email.return_value = True

        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )

        # Actualiza directamente en la base de datos (sin disparar auto_now)
        Exchange.objects.filter(id=exchange.id).update(
            updated_at=timezone.now() - timedelta(days=6)
        )
        exchange.refresh_from_db()

        success, message = ExchangeService.cancel_exchange(
            exchange_id=exchange.id,
            email_user=self.user1.email,
            reason="Test"
        )

        self.assertFalse(success)
        self.assertIn("5 días", message)

    
    def test_list_exchanges_offered_accepted(self):
        """Listar intercambios ofrecidos y aceptados"""
        # Crear varios intercambios
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        # Listar
        exchanges = ExchangeService.list_exchanges(
            email_user=self.user2.email,
            status_filter="accepted",
            exchanges_type="offered"
        )
        
        self.assertEqual(len(exchanges), 1)
    
    def test_list_exchanges_requested_pending(self):
        """Listar intercambios solicitados pendientes"""
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        exchanges = ExchangeService.list_exchanges(
            email_user=self.user1.email,
            status_filter="in_progress",
            exchanges_type="requested"
        )
        
        self.assertEqual(len(exchanges), 1)
    
    def test_list_exchanges_cancelled(self):
        """Listar intercambios cancelados"""
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.CANCELLED
        )
        
        exchanges = ExchangeService.list_exchanges(
            email_user=self.user1.email,
            status_filter="cancelled",
            exchanges_type="requested"
        )
        
        self.assertEqual(len(exchanges), 1)
    
    def test_list_exchanges_empty(self):
        """Listar cuando no hay intercambios"""
        exchanges = ExchangeService.list_exchanges(
            email_user=self.user1.email,
            status_filter="accepted",
            exchanges_type="requested"
        )
        
        self.assertEqual(len(exchanges), 0)


class ExchangeViewsTest(TestCase):
    """Tests para las vistas de Exchange"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuarios
        self.user1 = User.objects.create(
            name="Usuario1",
            email="user1@test.com",
            phone="1111111111",
            address="Dir 1"
        )
        self.user1.set_password("Password123!")
        self.user1.save()
        
        self.user2 = User.objects.create(
            name="Usuario2",
            email="user2@test.com",
            phone="2222222222",
            address="Dir 2"
        )
        self.user2.set_password("Password123!")
        self.user2.save()
        
        # Crear publicaciones
        self.pub1 = Publications.objects.create(
            user=self.user1,
            title="Libro de Python",
            description="Libro excelente",
        )
        
        self.pub2 = Publications.objects.create(
            user=self.user2,
            title="Laptop Dell",
            description="Laptop en buen estado",
        )
        
        # Generar tokens para user2
        tokens = JWTService.generate_tokens(self.user2)
        self.token = tokens['access']
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_create_exchange_success(self, mock_send_email):
        """Crear intercambio exitosamente"""
        mock_send_email.return_value = True
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('create_exchange')
        data = {
            "request_item": self.pub1.id,
            "offered_item": self.pub2.id,
            "status": Exchange.Status.PENDING
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
    
    def test_create_exchange_unauthenticated(self):
        """Crear intercambio sin autenticación"""
        url = reverse('create_exchange')
        data = {
            "request_item": self.pub1.id,
            "offered_item": self.pub2.id,
            "status": Exchange.Status.PENDING
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_create_exchange_invalid_publication(self, mock_send_email):
        """Crear intercambio con publicación inválida"""
        mock_send_email.return_value = True
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('create_exchange')
        data = {
            "request_item": 99999,
            "offered_item": self.pub2.id,
            "status": Exchange.Status.PENDING
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_respond_exchange_success(self, mock_send_email):
        """Responder a intercambio exitosamente"""
        mock_send_email.return_value = True
        
        # Crear intercambio
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('respond_exchange')
        data = {
            "exchange_id": exchange.id,
            "status": Exchange.Status.ACCEPTED
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verificar cambio de estado
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, Exchange.Status.ACCEPTED)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_respond_exchange_not_found(self, mock_send_email):
        """Responder a intercambio inexistente"""
        mock_send_email.return_value = True
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('respond_exchange')
        data = {
            "exchange_id": 99999,
            "status": Exchange.Status.ACCEPTED
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_success(self, mock_send_email):
        """Cancelar intercambio exitosamente"""
        mock_send_email.return_value = True
        
        # Crear intercambio aceptado
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        exchange.updated_at = timezone.now()
        exchange.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('cancel_exchange')
        data = {
            "exchange_id": exchange.id,
            "reason": "Ya no me interesa"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estado
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, Exchange.Status.CANCELLED)
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_cancel_exchange_not_accepted(self, mock_send_email):
        """No se puede cancelar si no está aceptado"""
        mock_send_email.return_value = True
        
        exchange = Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('cancel_exchange')
        data = {
            "exchange_id": exchange.id,
            "reason": "Test"
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_exchanges_success(self):
        """Listar intercambios exitosamente"""
        # Crear intercambios
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        url = reverse('list_exchanges')
        response = self.client.get(f'{url}?status=accepted&type=offered')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_list_exchanges_unauthenticated(self):
        """Listar intercambios sin autenticación"""
        url = reverse('list_exchanges')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_exchanges_with_filters(self):
        """Listar intercambios con filtros"""
        # Crear varios intercambios
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.ACCEPTED
        )
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.PENDING
        )
        Exchange.objects.create(
            requested_item=self.pub1,
            offered_item=self.pub2,
            status=Exchange.Status.CANCELLED
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('list_exchanges')
        
        # Test filtro accepted
        response = self.client.get(f'{url}?status=accepted&type=offered')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test filtro in_progress
        response = self.client.get(f'{url}?status=in_progress&type=offered')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test filtro cancelled
        response = self.client.get(f'{url}?status=cancelled&type=offered')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExchangeIntegrationTest(TestCase):
    """Tests de integración para flujo completo de intercambios"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuarios
        self.user1 = User.objects.create(
            name="Usuario1",
            email="user1@test.com",
            phone="1111111111",
            address="Dir 1"
        )
        self.user1.set_password("Password123!")
        self.user1.save()
        
        self.user2 = User.objects.create(
            name="Usuario2",
            email="user2@test.com",
            phone="2222222222",
            address="Dir 2"
        )
        self.user2.set_password("Password123!")
        self.user2.save()
        
        # Crear publicaciones
        self.pub1 = Publications.objects.create(
            user=self.user1,
            title="Libro",
            description="Libro excelente"
        )
        
        self.pub2 = Publications.objects.create(
            user=self.user2,
            title="Laptop",
            description="Laptop en buen estado"
        )
        
        # Tokens
        tokens1 = JWTService.generate_tokens(self.user1)
        tokens2 = JWTService.generate_tokens(self.user2)
        self.token1 = tokens1['access']
        self.token2 = tokens2['access']
    
    @patch('comunications.services.email_service.EmailService.send_email')
    def test_full_exchange_flow(self, mock_send_email):
        """Test de flujo completo: crear, aceptar, cancelar"""
        mock_send_email.return_value = True
        
        # 1. User2 crea oferta de intercambio
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('create_exchange')
        data = {
            "request_item": self.pub1.id,
            "offered_item": self.pub2.id,
            "status": Exchange.Status.PENDING
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        exchange_id = Exchange.objects.first().id
        
        # 2. User1 acepta la oferta
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('respond_exchange')
        data = {
            "exchange_id": exchange_id,
            "status": Exchange.Status.ACCEPTED
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. User1 cancela el intercambio
        url = reverse('cancel_exchange')
        data = {
            "exchange_id": exchange_id,
            "reason": "Cambié de opinión"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estado final
        exchange = Exchange.objects.get(id=exchange_id)
        self.assertEqual(exchange.status, Exchange.Status.CANCELLED)