from django import forms

from pos.models import Order, Menu

# New Order 
class BuatOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'meja',
            'pelanggan',
        ]

# Bayar
class BayarOrderForm(forms.Form):
    dibayar = forms.IntegerField()

# Menu
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nama', 'price', 'image']
        widgets = {
            'image': forms.URLInput(attrs={'placeholder': 'Masukkan URL gambar'})
        }

# Edit Menu
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nama','price', 'image']  # Tentukan field apa saja yang bisa di-edit

