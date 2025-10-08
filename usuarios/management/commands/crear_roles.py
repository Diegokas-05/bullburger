from django.core.management.base import BaseCommand
from usuarios.models import Rol

class Command(BaseCommand):
    help = 'Crea los roles iniciales del sistema'

    def handle(self, *args, **options):
        roles = ['Cliente', 'Empleado', 'Administrador']
        
        for rol_nombre in roles:
            rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Rol creado: {rol_nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Rol ya existía: {rol_nombre}')
                )