from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario, Rol
from django.contrib.auth.password_validation import validate_password

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

## === REEMPLAZA tu UsuarioAdminForm por este ===
class UsuarioAdminForm(forms.ModelForm):
    """
    Form para crear/editar administradores (o staff) desde modal.
    - En creación: contraseña requerida (password + password2).
    - En edición: contraseña opcional (si la llenas, se cambia).
    - Valida email único (ignorando el propio usuario al editar).
    - Ajusta flags según el rol elegido (puedes adaptar el mapping).
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        required=False,
        help_text='Dejar vacío para mantener la contraseña actual'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion', 'rol', 'is_active']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección',
                'rows': 3
            }),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # En creación (no hay PK): contraseña obligatoria
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'La contraseña es obligatoria para nuevos usuarios'
            self.fields['password2'].required = True
        else:
            # En edición: contraseña opcional
            self.fields['password'].required = False
            self.fields['password2'].required = False

    # --- Validaciones ---

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = Usuario.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un usuario registrado con este correo electrónico')
        return email

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('password')
        pwd2 = cleaned.get('password2')

        # En creación, ambas obligatorias; en edición, solo si llenan una:
        if (pwd or pwd2):
            if pwd != pwd2:
                raise ValidationError({'password2': 'Las contraseñas no coinciden'})
            if pwd and len(pwd) < 8:
                raise ValidationError({'password': 'La contraseña debe tener al menos 8 caracteres'})
            if pwd and pwd.isdigit():
                raise ValidationError({'password': 'La contraseña no puede contener solo números'})

        return cleaned

    # --- Persistencia ---

    def _aplicar_flags_por_rol(self, user: Usuario):
        """
        Ajusta is_staff / is_superuser según el rol.
        Adáptalo si tu lógica de roles es distinta.
        """
        try:
            nombre_rol = (user.rol.nombre or '').strip().lower()
        except Exception:
            nombre_rol = ''

        if nombre_rol == 'administrador':
            user.is_staff = True
            user.is_superuser = True
        elif nombre_rol == 'empleado':
            user.is_staff = True
            user.is_superuser = False
        else:  # cliente u otros
            user.is_staff = False
            user.is_superuser = False

    def save(self, commit=True):
        user = super().save(commit=False)

        # Si se proporcionó una nueva contraseña (en creación o edición)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)

        # Ajustar flags según el rol elegido
        self._aplicar_flags_por_rol(user)

        if commit:
            user.save()
        return user

# ========== PERFIL ==========
class PerfilForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario actual."""
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email':  forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección', 'rows': 3}),
        }


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
            'minlength': 8
        })
    )
    password_nueva2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    def __init__(self, user, *args, **kwargs):
        """
        Recibe el usuario autenticado para validar la contraseña actual
        y poder aplicar el cambio al guardar.
        """
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password_actual(self):
        old = self.cleaned_data.get('password_actual') or ''
        if not self.user.check_password(old):
            raise ValidationError('La contraseña actual no es correcta.')
        return old

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password_nueva') or ''
        p2 = cleaned.get('password_nueva2') or ''

        if p1 != p2:
            self.add_error('password_nueva2', 'Las contraseñas no coinciden.')

        # Evitar que sea igual a la actual
        if p1 and 'password_actual' in cleaned and p1 == cleaned.get('password_actual'):
            self.add_error('password_nueva', 'La nueva contraseña no puede ser igual a la actual.')

        # Validadores de Django (complejidad, longitud, etc.)
        if p1:
            try:
                validate_password(p1, self.user)
            except ValidationError as e:
                self.add_error('password_nueva', e.messages)

        return cleaned

    def save(self, commit=True):
        """
        Aplica el cambio de contraseña al usuario.
        Devuelve el usuario para poder usar update_session_auth_hash.
        """
        new_password = self.cleaned_data['password_nueva']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user