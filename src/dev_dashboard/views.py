from django.shortcuts import render
from django.http import JsonResponse
from django.urls import get_resolver
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.db import connection
import os
import sys
import django
from pathlib import Path


def dev_dashboard(request):
    """Головна сторінка dev dashboard"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    context = {
        'title': 'Development Dashboard',
        'project_name': 'WHMCS Admin Panel',
    }
    return render(request, 'dev_dashboard/dashboard.html', context)


def url_patterns_view(request):
    """Показує всі URL patterns проекту"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    def extract_urls(urlpatterns, prefix=''):
        urls = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # Include pattern
                urls.extend(extract_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # Regular URL pattern
                url_info = {
                    'pattern': prefix + str(pattern.pattern),
                    'name': getattr(pattern, 'name', None),
                    'view': None,
                    'methods': ['GET', 'POST']  # Default
                }
                
                if hasattr(pattern, 'callback'):
                    if hasattr(pattern.callback, '__name__'):
                        url_info['view'] = pattern.callback.__name__
                    elif hasattr(pattern.callback, 'view_class'):
                        url_info['view'] = pattern.callback.view_class.__name__
                    else:
                        url_info['view'] = str(pattern.callback)
                
                urls.append(url_info)
        return urls
    
    resolver = get_resolver()
    all_urls = extract_urls(resolver.url_patterns)
    
    context = {
        'urls': all_urls,
        'total_urls': len(all_urls)
    }
    return render(request, 'dev_dashboard/urls.html', context)


def apps_info_view(request):
    """Показує інформацію про всі Django apps"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    apps_info = []
    for app_config in apps.get_app_configs():
        models_info = []
        for model in app_config.get_models():
            models_info.append({
                'name': model.__name__,
                'table': model._meta.db_table,
                'fields_count': len(model._meta.fields),
                'fields': [f.name for f in model._meta.fields]
            })
        
        apps_info.append({
            'name': app_config.name,
            'label': app_config.label,
            'verbose_name': app_config.verbose_name,
            'path': str(app_config.path),
            'models': models_info,
            'models_count': len(models_info)
        })
    
    context = {
        'apps': apps_info,
        'total_apps': len(apps_info)
    }
    return render(request, 'dev_dashboard/apps.html', context)


def settings_view(request):
    """Показує налаштування Django"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    # Безпечні налаштування для показу
    safe_settings = {}
    sensitive_keys = ['SECRET_KEY', 'PASSWORD', 'KEY', 'TOKEN', 'API']
    
    for key in dir(settings):
        if not key.startswith('_') and key.isupper():
            value = getattr(settings, key)
            # Приховуємо чутливі дані
            if any(sensitive in key for sensitive in sensitive_keys):
                safe_settings[key] = '***HIDDEN***'
            else:
                safe_settings[key] = value
    
    context = {
        'settings': safe_settings,
        'debug': settings.DEBUG,
        'django_version': django.get_version(),
        'python_version': sys.version
    }
    return render(request, 'dev_dashboard/settings.html', context)


def database_info_view(request):
    """Показує інформацію про базу даних"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    db_info = {}
    
    # Інформація про підключення
    db_config = settings.DATABASES['default']
    db_info['engine'] = db_config['ENGINE']
    db_info['name'] = db_config['NAME']
    db_info['host'] = db_config.get('HOST', 'localhost')
    db_info['port'] = db_config.get('PORT', 'default')
    
    # Статистика таблиць
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
    
    # Кількість користувачів
    user_count = User.objects.count()
    
    context = {
        'db_info': db_info,
        'tables': tables,
        'tables_count': len(tables),
        'user_count': user_count
    }
    return render(request, 'dev_dashboard/database.html', context)


def translations_info_view(request):
    """Показує інформацію про переклади"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    locale_dir = Path(settings.BASE_DIR) / 'locale'
    languages_info = []
    
    for lang_code, lang_name in settings.LANGUAGES:
        po_file = locale_dir / lang_code / 'LC_MESSAGES' / 'django.po'
        mo_file = locale_dir / lang_code / 'LC_MESSAGES' / 'django.mo'
        
        lang_info = {
            'code': lang_code,
            'name': lang_name,
            'po_exists': po_file.exists(),
            'mo_exists': mo_file.exists(),
            'po_size': po_file.stat().st_size if po_file.exists() else 0,
            'mo_size': mo_file.stat().st_size if mo_file.exists() else 0,
        }
        
        # Статистика перекладів
        if po_file.exists():
            try:
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                total = len(re.findall(r'^msgid "([^"]*)"', content, re.MULTILINE))
                translated = len(re.findall(r'^msgstr "([^"]+)"', content, re.MULTILINE))
                empty = len(re.findall(r'^msgstr ""', content, re.MULTILINE))
                
                if total > 0:
                    total -= 1  # Subtract header
                    
                lang_info.update({
                    'total_strings': total,
                    'translated_strings': translated,
                    'empty_strings': empty,
                    'percentage': (translated * 100 // total) if total > 0 else 0
                })
            except Exception:
                lang_info.update({
                    'total_strings': 0,
                    'translated_strings': 0,
                    'empty_strings': 0,
                    'percentage': 0
                })
        
        languages_info.append(lang_info)
    
    context = {
        'languages': languages_info,
        'default_language': settings.LANGUAGE_CODE,
        'use_i18n': settings.USE_I18N,
        'locale_paths': settings.LOCALE_PATHS
    }
    return render(request, 'dev_dashboard/translations.html', context)


def system_info_view(request):
    """Показує системну інформацію"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Dev dashboard доступний тільки в DEBUG режимі'}, status=403)
    
    # Інформація про середовище
    env_info = {
        'python_version': sys.version,
        'django_version': django.get_version(),
        'debug_mode': settings.DEBUG,
        'base_dir': str(settings.BASE_DIR),
        'static_url': settings.STATIC_URL,
        'media_url': getattr(settings, 'MEDIA_URL', 'Not set'),
    }
    
    # Змінні середовища
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
            env_vars[key] = '***HIDDEN***'
        else:
            env_vars[key] = value
    
    context = {
        'env_info': env_info,
        'env_vars': dict(sorted(env_vars.items())),
        'installed_apps': settings.INSTALLED_APPS,
        'middleware': settings.MIDDLEWARE
    }
    return render(request, 'dev_dashboard/system.html', context)
