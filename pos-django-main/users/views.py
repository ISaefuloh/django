from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserUpdateForm
from django.contrib.auth.models import Group


def bukan_level_kasir(user):
    # Memeriksa apakah user bukan bagian dari grup Level_Kasir
    return not user.groups.filter(name='Level_Kasir').exists()

@login_required
@user_passes_test(bukan_level_kasir, login_url='pos:home')  # Hanya pengguna bukan 'Level_Kasir' yang bisa mengakses
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = form.cleaned_data['group']
            user.groups.add(group)
            login(request, user)
            return redirect('pos:home')  # Halaman utama setelah login
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('pos:home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# LogoutView adalah view bawaan Django
class CustomLogoutView(LogoutView):
    next_page = 'users:login'  # Ganti dengan URL tujuan setelah logout (misalnya halaman login)

# Edit Profile
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

# Pengaturan hak akses
@login_required
def assign_group(request):
    user = request.user
    group = Group.objects.get(name='admin')  # Misalnya grup 'admin'
    user.groups.add(group)
    return redirect('profile')

# Halaman home setelah berhasil login
def welcome(request):
    return render(request, 'users/welcome.html')


