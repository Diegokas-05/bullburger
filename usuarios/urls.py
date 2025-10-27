from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_cliente_view, name='registro_cliente'),

    # Dashboards
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),

    # Clientes
    path('administrador/clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Empleados
     path('administrador/empleados/', views.lista_empleados, name='lista_empleados'),
     path('empleados/editar/<int:id>/', views.editar_empleado, name='editar_empleado'),
     path('empleados/eliminar/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),
     path('empleados/crear/', views.crear_empleado, name='crear_empleado'),


    # Administradores

    path('administrador/administradores/', views.lista_administradores, name='lista_administradores'),
    path('administradores/crear/', views.crear_administrador, name='crear_administrador'),
    path('administradores/editar/<int:id>/', views.editar_administrador, name='editar_administrador'),
    path('administradores/eliminar/<int:id>/', views.eliminar_administrador, name='eliminar_administrador'),

]
