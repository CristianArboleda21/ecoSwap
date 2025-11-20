import base64
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from publications.models import Publications, Category, State, Condition, PublicationImage, FavoritePublication
from users.models import UserApp


class PublicationsTestCase(APITestCase):
    def setUp(self):
        self.user = UserApp.objects.create(
            email="test@example.com",
            name="Test User",
            phone="3000000000",
            address="Test Address",
        )
        self.user.set_password("123456")
        self.user.save()
        self.client.force_authenticate(self.user)

        self.category = Category.objects.create(nombre="Electrónica")
        self.state = State.objects.create(nombre="Nuevo")
        self.condition = Condition.objects.create(nombre="Perfecto")

    def test_create_publication(self):
        url = reverse('create_publication')
        data = {
            "titulo": "Laptop",
            "descripcion": "Buena laptop",
            "categoria_id": self.category.id,
            "estado_id": self.state.id,
            "ubicacion": "Bogotá",
            "condicion_id": self.condition.id,
            "imagenes": []
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Publications.objects.filter(titulo="Laptop").exists())

    def test_create_publication_missing_required_fields(self):
        url = reverse('create_publication')
        data = {"titulo": "Faltan cosas"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_publication(self):
        pub = Publications.objects.create(
            user=self.user,
            categoria=self.category,
            estado=self.state,
            condition=self.condition,
            titulo="Original",
            descripcion="Desc",
            ubicacion="Medellín",
        )

        url = reverse('edit_publication', args=[pub.id])
        data = {"titulo": "Modificado"}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pub.refresh_from_db()
        self.assertEqual(pub.titulo, "Modificado")

    def test_get_publication(self):
        pub = Publications.objects.create(
            user=self.user,
            categoria=self.category,
            estado=self.state,
            condition=self.condition,
            titulo="Consulta",
            descripcion="Desc",
            ubicacion="Cali",
        )

        url = reverse('get_publication', args=[pub.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["publication"]["titulo"], "Consulta")

    def test_add_favorite(self):
        pub = Publications.objects.create(
            user=self.user,
            categoria=self.category,
            estado=self.state,
            condition=self.condition,
            titulo="Favorito",
            descripcion="Desc",
            ubicacion="Bogotá",
        )

        url = reverse('add_favorite', args=[pub.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(FavoritePublication.objects.filter(user=self.user, publicacion=pub).exists())

    def test_remove_favorite(self):
        pub = Publications.objects.create(
            user=self.user,
            categoria=self.category,
            estado=self.state,
            condition=self.condition,
            titulo="Quitar",
            descripcion="Desc",
            ubicacion="Bogotá",
        )

        FavoritePublication.objects.create(user=self.user, publicacion=pub)

        url = reverse('remove_favorite', args=[pub.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(FavoritePublication.objects.filter(user=self.user, publicacion=pub).exists())

    def test_list_user_publications(self):
        Publications.objects.create(
            user=self.user,
            categoria=self.category,
            estado=self.state,
            condition=self.condition,
            titulo="Pub1",
            descripcion="Desc",
            ubicacion="Bogotá",
        )
        url = reverse('list_user_publications')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["publications"]), 1)

    def test_create_category(self):
        url = reverse('create_category')
        data = {"nombre": "Hogar"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(nombre="Hogar").exists())

    def test_list_categories(self):
        url = reverse('list_categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["categories"]), 1)

    def test_get_category(self):
        url = reverse('get_category', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_state(self):
        url = reverse('create_state')
        data = {"nombre": "Usado"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(State.objects.filter(nombre="Usado").exists())

    def test_list_states(self):
        url = reverse('list_states')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_state(self):
        url = reverse('get_state', args=[self.state.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_condition(self):
        url = reverse('list_condition')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_condition(self):
        url = reverse('get_condition', args=[self.condition.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
