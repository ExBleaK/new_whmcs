from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings


def admin_login(request):
    """Форма авторизації адміністратора"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Невірний логін або пароль, або у вас немає прав адміністратора')
    
    return render(request, 'admin_panel/login.html', {
        'debug': settings.DEBUG
    })


@login_required
def admin_dashboard(request):
    """Головна сторінка приватного кабінету"""
    if not request.user.is_staff:
        messages.error(request, 'У вас немає прав доступу до адміністративної панелі')
        return redirect('admin_login')
    
    return render(request, 'admin_panel/dashboard.html', {
        'user': request.user,
        'debug': settings.DEBUG
    })


@login_required
def admin_profile(request):
    """Налаштування профілю адміністратора"""
    if not request.user.is_staff:
        messages.error(request, 'У вас немає прав доступу до адміністративної панелі')
        return redirect('admin_login')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Профіль успішно оновлено')
        return redirect('admin_profile')
    
    return render(request, 'admin_panel/profile.html', {
        'user': request.user,
        'debug': settings.DEBUG
    })


def admin_logout(request):
    """Вихід з системи"""
    logout(request)
    messages.success(request, 'Ви успішно вийшли з системи')
    return redirect('admin_login')