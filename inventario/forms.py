# inventario/forms.py
from django import forms
from .models import Ingrediente, Receta

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = [
            'nombre', 'descripcion', 'unidad_medida', 
            'precio_paquete', 'tamaño_paquete',
            'stock_actual', 'stock_minimo', 
            'proveedor', 'ubicacion'
        ]
        # REMOVED 'costo_unitario' - it's a calculated property
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ingrediente'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional...'
            }),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'precio_paquete': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tamaño_paquete': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '1.00'
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '10'
            }),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación en almacén'
            }),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras y espacios")
        return nombre.strip()
    
    def clean_precio_paquete(self):
        precio = self.cleaned_data.get('precio_paquete')
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo")
        return precio
    
    def clean_tamaño_paquete(self):
        tamaño = self.cleaned_data.get('tamaño_paquete')
        if tamaño <= 0:
            raise forms.ValidationError("El tamaño del paquete debe ser mayor a 0")
        return tamaño
    
    def clean_stock_actual(self):
        stock = self.cleaned_data.get('stock_actual')
        if stock < 0:
            raise forms.ValidationError("El stock actual no puede ser negativo")
        return stock
    
    def clean_stock_minimo(self):
        stock = self.cleaned_data.get('stock_minimo')
        if stock < 0:
            raise forms.ValidationError("El stock mínimo no puede ser negativo")
        return stock

# El resto de tus forms permanecen igual...
class AjusteInventarioForm(forms.Form):
    cantidad_nueva = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['ingrediente', 'cantidad', 'notas']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas opcionales...'}),
        }