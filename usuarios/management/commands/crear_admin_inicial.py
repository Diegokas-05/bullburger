from django.core.management.base import BaseCommand
from usuarios.models import Usuario, Rol
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea el usuario administrador inicial'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Asegurarse de que existan los roles
            rol_admin, created = Rol.objects.get_or_create(nombre='Administrador')
            
            # Crear admin si no existe
            if not Usuario.objects.filter(email='admin@bullburger.com').exists():
                admin = Usuario.objects.create_superuser(
                    email='admin@bullburger.com',
                    password='admin123',
                    nombre='Administrador Principal',
                    rol=rol_admin
                )
                self.stdout.write(
                    self.style.SUCCESS('Admin creado: aaron@gmail.com / admin123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('El admin ya existe')
                )