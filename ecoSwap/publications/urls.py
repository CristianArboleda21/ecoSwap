from django.urls import path
from publications.views import views

urlpatterns = [
    # Publicaciones
    path('create', views.create_publication, name='create_publication'),
    path('edit/<int:pub_id>', views.edit_publication, name='edit_publication'),
    path('list', views.list_publications, name='list_publications'),
    path('<int:pub_id>', views.get_publication, name='get_publication'),
    path('category/<int:categoria_id>', views.publications_by_category, name='publications_by_category'),

    # Favoritos
    path('favorites/add/<int:pub_id>', views.add_favorite, name='add_favorite'),
    path('favorites/remove/<int:pub_id>', views.remove_favorite, name='remove_favorite'),
    path('favorites/list', views.list_user_favorites, name='list_user_favorites'),

    # Publicaciones del usuario
    path('user/publications', views.list_user_publications, name='list_user_publications'),


    # Categorias
    path('categories/create', views.create_category, name='create_category'),
    path('categories/list', views.list_categories, name='list_categories'),
    path('categories/<int:categoria_id>/', views.get_category, name='get_category'),

    # Estados
    path('states/create', views.create_state, name='create_state'),
    path('states/list', views.list_states, name='list_states'),
    path('states/<int:estado_id>/', views.get_state, name='get_state'),
]
