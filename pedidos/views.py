from django.shortcuts import render
from pedidos import views as pedidos_views

urlpatterns = [
    # ... otras URLs ...
    path('empleado/pedidos/', pedidos_views.gestion_pedidos, name='gestion_pedidos'),
    path('empleado/pedidos/actualizar-estado/<int:pedido_id>/', pedidos_views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
]