"""
URL configuration for whmcs_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.shortcuts import redirect
from django.http import Http404
from django.conf.urls.i18n import i18n_patterns

def redirect_to_admin_panel(request):
    return redirect('admin_login')

def admin_disabled(request):
    """Заборонити доступ до стандартної Django адмінки"""
    raise Http404("Page not found")

urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Відключаємо стандартну Django адмінку для безпеки
    path('admin/', admin_disabled),
    path('panel/', include('admin_panel.urls')),
    path('', redirect_to_admin_panel),
    prefix_default_language=False
)
