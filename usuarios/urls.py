from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_cliente_view, name='registro_cliente'),
    
    # Dashboards - CAMBIADO: usar 'administrador' en lugar de 'admin'
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
]