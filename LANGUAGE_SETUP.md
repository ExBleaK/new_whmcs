# Налаштування мультимовності в WHMCS Admin Panel

## Підтримувані мови

- **Англійська (en)** - мова за замовчуванням
- **Українська (uk)** - повний переклад інтерфейсу

## Як працює перемикання мови

### 1. На сторінці входу
- Перемикач мови розташований над формою входу
- Вибрана мова зберігається в сесії користувача

### 2. В адмін панелі
- Перемикач мови знаходиться в навігаційному меню (іконка глобуса)
- Мова змінюється миттєво без перезавантаження сторінки

## Технічні деталі

### Налаштування Django
```python
# settings.py
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('uk', 'Українська'),
]
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### Middleware
```python
MIDDLEWARE = [
    # ...
    'django.middleware.locale.LocaleMiddleware',
    # ...
]
```

### URL конфігурація
```python
# urls.py
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # ваші URL-и тут
    prefix_default_language=False
)
```

## Додавання нових перекладів

### 1. Створення файлів перекладів
```bash
cd src
python manage.py makemessages -l [код_мови]
```

### 2. Редагування перекладів
Відредагуйте файл `src/locale/[код_мови]/LC_MESSAGES/django.po`

### 3. Компіляція перекладів
```bash
python manage.py compilemessages
```

## Використання в шаблонах

### Завантаження тегів
```html
{% load i18n %}
```

### Простий переклад
```html
{% trans "Text to translate" %}
```

### Переклад з змінними
```html
{% blocktrans with name=user.username %}Welcome, {{ name }}!{% endblocktrans %}
```

### Перемикач мови
```html
{% get_current_language as LANGUAGE_CODE %}
{% get_available_languages as LANGUAGES %}
{% get_language_info_list for LANGUAGES as languages %}
{% for language in languages %}
    <form action="{% url 'set_language' %}" method="post">
        {% csrf_token %}
        <input name="next" type="hidden" value="{{ request.get_full_path }}" />
        <input name="language" type="hidden" value="{{ language.code }}" />
        <button type="submit">{{ language.name_local }}</button>
    </form>
{% endfor %}
```

## Структура файлів

```
src/
├── locale/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── django.po
│   │       └── django.mo
│   └── uk/
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
└── ...
```

## Тестування

1. Запустіть сервер: `python manage.py runserver`
2. Відкрийте http://localhost:8000
3. Перемкніть мову на сторінці входу
4. Увійдіть в систему та перевірте перемикач в навігації

## Додавання нової мови

1. Додайте мову в `LANGUAGES` в `settings.py`
2. Створіть переклади: `python manage.py makemessages -l [код_мови]`
3. Заповніть файл `django.po`
4. Скомпілюйте: `python manage.py compilemessages`
5. Перезапустіть сервер

## Примітки

- Мова зберігається в сесії користувача
- При першому відвідуванні використовується мова браузера або мова за замовчуванням
- Всі статичні тексти в шаблонах обгорнуті в теги перекладу
- URL-и автоматично префіксуються кодом мови (крім мови за замовчуванням)