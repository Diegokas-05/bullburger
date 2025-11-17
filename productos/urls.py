# productos/urls.py
from django.urls import path
from . import views  # Asegúrate de que 'views' esté importado

urlpatterns = [
    path('administrador/menu/', views.lista_productos, name='menu_administrador'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('categoria/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),

    # Cliente / Carrito
    path('cliente/menu_cliente/', views.menu_cliente, name='menu_cliente'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('cliente/carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/editar/<int:item_id>/', views.editar_cantidad, name='editar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/checkout/', views.carrito_checkout, name='carrito_checkout'),
    
    # ==========================================================
    # ✅ ¡AQUÍ ESTÁ LA LÍNEA QUE FALTA! ✅
    # Añade esta ruta para la API que carga los datos de edición:
    path('api/producto/<int:producto_id>/', views.api_detalle_producto_edicion, name='api_detalle_producto_edicion'),
    # ==========================================================
    
    path('api/stock/', views.api_stock_productos, name='api_stock'),
    path("api/stock/<int:producto_id>/", views.api_stock_producto, name="api_stock_producto"),
]