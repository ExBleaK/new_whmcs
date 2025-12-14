from django.urls import path
from . import views

app_name = 'dev_dashboard'

urlpatterns = [
    path('', views.dev_dashboard, name='dashboard'),
    path('urls/', views.url_patterns_view, name='urls'),
    path('apps/', views.apps_info_view, name='apps'),
    path('settings/', views.settings_view, name='settings'),
    path('database/', views.database_info_view, name='database'),
    path('translations/', views.translations_info_view, name='translations'),
    path('system/', views.system_info_view, name='system'),
]