from comunications.services.email_service import EmailService
from django.utils import timezone
from ..serializers import PublicationsSerializer
from publications.models import Publications, UserApp, Category, State, PublicationImage
from django.utils import timezone
from ..models import Publications, FavoritePublication

class PublicationsService:


    @classmethod
    def create_publication(cls, user_id, categoria_id, estado_id, titulo, descripcion, ubicacion, imagenes):
        # Validar usuario
        try:
            user = UserApp.objects.get(id=user_id)
        except UserApp.DoesNotExist:
            return False, "El usuario no existe."

        # Validar categoría
        try:
            categoria = Category.objects.get(id=categoria_id)
        except Category.DoesNotExist:
            return False, "La categoría no existe."

        # Validar estado
        try:
            estado = State.objects.get(id=estado_id)
        except State.DoesNotExist:
            return False, "El estado no existe."

        # Crear publicación
        publicacion = Publications.objects.create(
            user=user,
            categoria=categoria,
            estado=estado,
            titulo=titulo,
            descripcion=descripcion,
            ubicacion=ubicacion,
            fecha_publicacion=timezone.now()
        )

        # Guardar imágenes si existen
        if imagenes:
            for img in imagenes:
                PublicationImage.objects.create(
                    publicacion=publicacion,
                    imagen=img
                )

        return True, "Publicación creada correctamente.", publicacion.id_publicacion


    @classmethod
    def update_publication(
        cls, 
        pub_id, 
        categoria_id=None, 
        estado_id=None, 
        titulo=None, 
        descripcion=None, 
        ubicacion=None, 
        nuevas_imagenes=None
    ):
        try:
            publicacion = Publications.objects.get(id_publicacion=pub_id)
        except Publications.DoesNotExist:
            return False, "La publicación no existe."

        if categoria_id:
            try:
                publicacion.categoria = Category.objects.get(id=categoria_id)
            except Category.DoesNotExist:
                return False, "La categoría no existe."

        if estado_id:
            try:
                publicacion.estado = State.objects.get(id=estado_id)
            except State.DoesNotExist:
                return False, "El estado no existe."

        if titulo:
            publicacion.titulo = titulo

        if descripcion:
            publicacion.descripcion = descripcion

        if ubicacion:
            publicacion.ubicacion = ubicacion

        publicacion.save()

        # Agregar imágenes nuevas
        if nuevas_imagenes:
            for img in nuevas_imagenes:
                PublicationImage.objects.create(publicacion=publicacion, imagen=img)

        return True, "Publicación actualizada correctamente."

    @classmethod
    def list_publications(cls, estado_id=None):
        publicaciones = Publications.objects.all()

        if estado_id:
            publicaciones = publicaciones.filter(estado_id=estado_id)

        return True, publicaciones

    @classmethod
    def get_publication(cls, pub_id):
        try:
            publicacion = Publications.objects.get(id_publicacion=pub_id)
            return True, publicacion
        except Publications.DoesNotExist:
            return False, "La publicación no existe."
    
    @classmethod
    def list_publications_by_category(cls, categoria_id):
        publicaciones = Publications.objects.filter(categoria_id=categoria_id)
        return True, publicaciones

    @classmethod
    def add_favorite(cls, user_id, pub_id):
        try:
            user = UserApp.objects.get(id=user_id)
        except UserApp.DoesNotExist:
            return False, "El usuario no existe."

        try:
            publication = Publications.objects.get(id_publicacion=pub_id)
        except Publications.DoesNotExist:
            return False, "La publicación no existe."

        fav, created = FavoritePublication.objects.get_or_create(
            user=user,
            publicacion=publication
        )

        if not created:
            return False, "La publicación ya está en favoritos."

        return True, "Agregado a favoritos."
    
    @classmethod
    def remove_favorite(cls, user_id, pub_id):
        try:
            fav = FavoritePublication.objects.get(
                user_id=user_id,
                publicacion_id=pub_id
            )
        except FavoritePublication.DoesNotExist:
            return False, "La publicación no está en favoritos."

        fav.delete()
        return True, "Eliminado de favoritos."

    @classmethod
    def list_favorites(cls, user_id):
        favoritos = FavoritePublication.objects.filter(user_id=user_id)
        publicaciones = [f.publicacion for f in favoritos]
        return True, publicaciones
    
    @classmethod
    def create_category(cls, nombre):
        # Validar si existe
        if Category.objects.filter(nombre=nombre).exists():
            return False, "La categoría ya existe."

        categoria = Category.objects.create(nombre=nombre)
        return True, "Categoría creada correctamente.", categoria.id
    
    @classmethod
    def list_categories(cls):
        categorias = Category.objects.all()
        return True, categorias

    @classmethod
    def get_category(cls, categoria_id):
        try:
            categoria = Category.objects.get(id=categoria_id)
            return True, categoria
        except Category.DoesNotExist:
            return False, "La categoría no existe."
        
    @classmethod
    def list_states(cls):
        estados = State.objects.all()
        return True, estados

    @classmethod
    def get_state(cls, estado_id):
        try:
            estado = State.objects.get(id=estado_id)
            return True, estado
        except State.DoesNotExist:
            return False, "El estado no existe."
        
    @classmethod
    def create_state(cls, nombre):
        # Validar si existe
        if State.objects.filter(nombre=nombre).exists():
            return False, "El estado ya existe."

        estado = State.objects.create(nombre=nombre)
        return True, "Estado creado correctamente.", estado.id

