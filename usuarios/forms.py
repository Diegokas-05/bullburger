from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario, Rol

class RegistroClienteForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'}),
        error_messages={
            'required': 'El nombre completo es obligatorio',
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Por favor introduce un correo electrónico válido',
        }
    )
    telefono = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'})
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tu dirección', 'rows': 3})
    )
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar los placeholders de las contraseñas
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        
        # Personalizar mensajes de error de contraseñas
        self.fields['password1'].error_messages = {
            'required': 'La contraseña es obligatoria',
        }
        self.fields['password2'].error_messages = {
            'required': 'Debes confirmar tu contraseña',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario registrado con este correo electrónico')
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError('La contraseña debe tener al menos 8 caracteres')
            
            # Verificar si es una contraseña común
            common_passwords = [
                '12345678', 'password', 'contraseña', 'qwerty', '11111111',
                '00000000', '123456789', 'password1', 'abc123', 'admin123'
            ]
            if password1.lower() in common_passwords:
                raise ValidationError('Esta contraseña es demasiado común, elige una más segura')
            
            # Verificar si es solo numérica
            if password1.isdigit():
                raise ValidationError('La contraseña no puede contener solo números')
        
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': 'Las contraseñas no coinciden'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.nombre = self.cleaned_data['nombre']
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        
        # Asignar rol de Cliente
        try:
            rol_cliente = Rol.objects.get(nombre='Cliente')
            user.rol = rol_cliente
        except Rol.DoesNotExist:
            # Si no existe el rol, crear uno
            rol_cliente = Rol.objects.create(nombre='Cliente')
            user.rol = rol_cliente
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Por favor introduce un correo electrónico válido',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        error_messages={
            'required': 'La contraseña es obligatoria',
        }
    )