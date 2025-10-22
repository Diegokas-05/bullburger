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
    path('administrador/clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

]