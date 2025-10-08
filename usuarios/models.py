from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    username = None
    email = models.EmailField('Correo Electrónico', unique=True)
    nombre = models.CharField('Nombre Completo', max_length=100)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    direccion = models.TextField('Dirección', blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.email})"

    def es_administrador(self):
        return self.rol and self.rol.nombre == 'Administrador'
    
    def es_empleado(self):
        return self.rol and self.rol.nombre == 'Empleado'
    
    def es_cliente(self):
        return self.rol and self.rol.nombre == 'Cliente'