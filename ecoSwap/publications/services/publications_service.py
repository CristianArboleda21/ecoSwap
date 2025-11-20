import base64
from django.core.files.base import ContentFile
import uuid
from django.utils import timezone
from publications.models import Publications, UserApp, Category, State, PublicationImage, Condition
from django.utils import timezone
from ..models import Publications, FavoritePublication


class PublicationsService:


    @classmethod
    def create_publication(cls, user_id, categoria_id, estado_id, titulo, descripcion, ubicacion, condicion_id, imagenes):
        # Validar usuario
        try:
            user = UserApp.objects.get(id=user_id)
        except UserApp.DoesNotExist:
            return False, "El usuario no existe.", None

        # Validar categoría
        try:
            categoria = Category.objects.get(id=categoria_id)
        except Category.DoesNotExist:
            return False, "La categoría no existe.", None

        # Validar estado
        try:
            estado = State.objects.get(id=estado_id)
        except State.DoesNotExist:
            return False, "El estado no existe.", None
        
        # Validar condicion (puede ser None)
        condition = None
        if condicion_id:
            try:
                condition = Condition.objects.get(id=condicion_id)
            except Condition.DoesNotExist:
                return False, "La condición no existe.", None

        # Crear publicación
        publicacion = Publications.objects.create(
            user=user,
            categoria=categoria,
            estado=estado,
            condition=condition,
            titulo=titulo,
            descripcion=descripcion,
            ubicacion=ubicacion,
            fecha_publicacion=timezone.now()
        )

        # Guardar imágenes si existen
        if imagenes:
            # Validar que sea una lista
            if not isinstance(imagenes, list):
                imagenes = [imagenes]
            
            # Límite de tamaño por imagen (10MB en base64)
            MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
            
            for img in imagenes:
                try:
                    # Si es un archivo (desde FormData), convertir a base64
                    if hasattr(img, 'read'):
                        img_data = img.read()
                        
                        # Validar tamaño
                        if len(img_data) > MAX_IMAGE_SIZE:
                            publicacion.delete()  # Eliminar publicación si hay error
                            return False, f"La imagen es demasiado grande. Tamaño máximo: 10MB", None
                        
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        # Determinar el tipo MIME
                        content_type = img.content_type if hasattr(img, 'content_type') else 'image/jpeg'
                        img_base64_string = f"data:{content_type};base64,{img_base64}"
                        
                        PublicationImage.objects.create(
                            publicacion=publicacion,
                            imagen=img_base64_string
                        )
                    # Si ya es una cadena base64
                    elif isinstance(img, str):
                        # Validar que contenga base64
                        if 'base64' not in img:
                            continue  # Saltar imágenes inválidas
                        
                        # Validar tamaño aproximado de la cadena
                        if len(img) > MAX_IMAGE_SIZE * 1.5:  # Base64 aumenta ~33% el tamaño
                            publicacion.delete()  # Eliminar publicación si hay error
                            return False, f"La imagen es demasiado grande. Tamaño máximo: 10MB", None
                        
                        PublicationImage.objects.create(
                            publicacion=publicacion,
                            imagen=img
                        )
                except Exception as img_error:
                    # Log del error
                    print(f"Error procesando imagen: {str(img_error)}")
                    continue

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
        condicion_id=None, 
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
        
        if condicion_id:
            try:
                publicacion.condition = Condition.objects.get(id=condicion_id)
            except Condition.DoesNotExist:
                return False, "La condición no existe."

        if titulo:
            publicacion.titulo = titulo

        if descripcion:
            publicacion.descripcion = descripcion

        if ubicacion:
            publicacion.ubicacion = ubicacion

        publicacion.save()

        # Reemplazar imágenes existentes
        if nuevas_imagenes is not None:
            try:
                # Eliminar imágenes actuales
                PublicationImage.objects.filter(publicacion=publicacion).delete()

                # Validar que sea una lista
                if not isinstance(nuevas_imagenes, list):
                    nuevas_imagenes = [nuevas_imagenes]

                # Límite de tamaño por imagen (10MB en base64)
                MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

                for img in nuevas_imagenes:
                    try:
                        # Si es un archivo (desde FormData), convertir a base64
                        if hasattr(img, 'read'):
                            img_data = img.read()
                            
                            # Validar tamaño
                            if len(img_data) > MAX_IMAGE_SIZE:
                                return False, f"La imagen es demasiado grande. Tamaño máximo: 10MB"
                            
                            img_base64 = base64.b64encode(img_data).decode('utf-8')
                            content_type = img.content_type if hasattr(img, 'content_type') else 'image/jpeg'
                            img_base64_string = f"data:{content_type};base64,{img_base64}"
                            
                            PublicationImage.objects.create(
                                publicacion=publicacion,
                                imagen=img_base64_string
                            )
                        # Si ya es una cadena base64
                        elif isinstance(img, str):
                            # Validar que contenga base64
                            if 'base64' not in img:
                                continue  # Saltar imágenes inválidas
                            
                            # Validar tamaño aproximado de la cadena
                            if len(img) > MAX_IMAGE_SIZE * 1.5:  # Base64 aumenta ~33% el tamaño
                                return False, f"La imagen es demasiado grande. Tamaño máximo: 10MB"
                            
                            PublicationImage.objects.create(
                                publicacion=publicacion,
                                imagen=img
                            )
                    except Exception as img_error:
                        # Log del error pero continuar con otras imágenes
                        print(f"Error procesando imagen: {str(img_error)}")
                        continue
                        
            except Exception as e:
                return False, f"Error al procesar las imágenes: {str(e)}"

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
    def list_user_publications(cls, user_id):
        publicaciones = Publications.objects.filter(user_id=user_id)
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
    
    @classmethod
    def list_condition(cls):
        condiciones = Condition.objects.all()
        return True, condiciones

    @classmethod
    def get_conditios(cls, condition_id):
        try:
            condicion = Condition.objects.get(id=condition_id)
            return True, condicion
        except State.DoesNotExist:
            return False, "El estado no existe."

