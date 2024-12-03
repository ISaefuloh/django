from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # Menambahkan pilihan untuk memilih grup
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Pilih Grup")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
