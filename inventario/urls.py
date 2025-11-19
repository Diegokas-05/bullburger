# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('administrador/inventario/', views.lista_inventario, name='inventario'),
    path('inventario/ingrediente/crear/', views.crear_ingrediente, name='crear_ingrediente'),
    path('inventario/ingrediente/editar/<int:ingrediente_id>/', views.editar_ingrediente, name='editar_ingrediente'),
    path('inventario/ingrediente/eliminar/<int:ingrediente_id>/', views.eliminar_ingrediente, name='eliminar_ingrediente'),
    path('inventario/ajustar/<int:ingrediente_id>/', views.ajustar_inventario, name='ajustar_inventario'),
    path('inventario/historial/', views.historial_inventario, name='historial_inventario'),
    # API endpoints
    path('inventario/api/ingrediente/<int:ingrediente_id>/', views.get_ingrediente_data, name='get_ingrediente_data'),
    path('empleado/', views.inventario_empleado, name='inventario_empleado'),
]