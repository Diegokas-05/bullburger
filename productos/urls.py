from django.urls import path
from . import views

urlpatterns = [
    path('administrador/menu/', views.lista_productos, name='menu_administrador'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('categoria/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # ...
    path('cliente/menu_cliente/', views.menu_cliente, name='menu_cliente'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('cliente/carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/editar/<int:item_id>/', views.editar_cantidad, name='editar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),

    
]