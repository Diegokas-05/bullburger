from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('categoria/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
]