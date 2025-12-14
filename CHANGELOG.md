# Changelog

Всі важливі зміни в цьому проекті будуть документовані в цьому файлі.

Формат базується на [Keep a Changelog](https://keepachangelog.com/uk/1.0.0/),
і цей проект дотримується [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Ініціалізація Django 6.0 проекту з PostgreSQL
- Docker конфігурація з PostgreSQL 16 та Django
- Приватний кабінет адміністратора з авторизацією
- Система управління користувачами через змінні оточення
- Management команда для створення адміністратора
- Налаштування безпеки та захист від стандартних атак

### Security
- Відключено стандартну Django адмін панель для безпеки
- Додано XSS та CSRF захист
- Налаштовано безпечні cookies та сесії
- Обмежено час сесії до 1 години
- Додано Content-Type та X-Frame захист

### Changed
- Замінено SQLite на PostgreSQL як основну базу даних
- Налаштовано змінні оточення для всіх конфігурацій
- Створено власну систему авторизації замість Django admin

## [0.1.0] - 2024-12-14

### Added
- Початкова структура проекту
- Віртуальне оточення Python 3.13
- Django 6.0 з PostgreSQL підтримкою
- Docker та Docker Compose конфігурація
- Базова документація в README.md

#### Структура проекту
```
new_whmcs/
├── src/                           # Django додаток
│   ├── whmcs_project/            # Основні налаштування Django
│   │   ├── settings.py           # Налаштування з PostgreSQL та безпекою
│   │   ├── urls.py               # URL маршрути (Django admin відключено)
│   │   └── ...
│   ├── admin_panel/              # Приватний кабінет адміністратора
│   │   ├── views.py              # Авторизація та управління профілем
│   │   ├── urls.py               # Маршрути панелі управління
│   │   ├── templates/            # HTML шаблони з Bootstrap 5
│   │   └── management/commands/  # Команда створення адміністратора
│   ├── .env                      # Змінні оточення (не в git)
│   └── .env.example              # Приклад змінних оточення
├── docker/                       # Docker конфігурація
│   ├── Dockerfile                # Django контейнер
│   └── docker-compose.yml        # Оркестрація сервісів
├── venv/                         # Python віртуальне оточення
├── requirements.txt              # Python залежності
└── README.md                     # Документація проекту
```

#### Функціонал адмін панелі
- **Авторизація**: Форма входу з перевіркою прав `is_staff`
- **Панель управління**: Статистика та швидкі дії
- **Профіль**: Редагування особистих даних (ім'я, прізвище, email)
- **Безпека**: Захищені маршрути з `@login_required`
- **UI/UX**: Адаптивний дизайн з Bootstrap 5 та Font Awesome

#### Технології
- **Backend**: Python 3.13, Django 6.0
- **База даних**: PostgreSQL 16
- **Контейнеризація**: Docker & Docker Compose
- **Frontend**: Bootstrap 5, Font Awesome 6
- **Безпека**: python-decouple для змінних оточення

#### Налаштування безпеки
- Django admin панель повністю відключена
- XSS та Content-Type захист
- CSRF токени для всіх форм
- Безпечні HTTP-only cookies
- Сесії з обмеженим часом життя (1 година)
- X-Frame-Options: DENY для захисту від clickjacking

#### Змінні оточення
```env
# Основні налаштування
DEBUG=1
SECRET_KEY=your-secret-key-here

# База даних PostgreSQL
DB_NAME=whmcs_db
DB_USER=whmcs_user
DB_PASSWORD=whmcs_password
DB_HOST=localhost
DB_PORT=5432

# Адміністратор системи
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@whmcs.local
```

#### Команди для розробки
```bash
# Повний запуск в Docker
cd docker && docker-compose up --build

# Локальна розробка
source venv/bin/activate
cd src && python manage.py runserver

# Створення адміністратора
python manage.py create_admin

# Міграції
python manage.py migrate
```

### Security Notes
- Стандартна Django `/admin/` панель недоступна (404)
- Доступ тільки через `/panel/` для авторизованих користувачів
- Всі паролі та ключі винесені в змінні оточення
- Автоматичне створення адміністратора з безпечними налаштуваннями