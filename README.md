# WHMCS Django Project

Django проект з PostgreSQL базою даних, налаштований для роботи в Docker контейнерах.

## Структура проекту

```
new_whmcs/
├── src/                    # Django додаток
│   ├── whmcs_project/     # Основні налаштування Django
│   ├── manage.py          # Django management команди
│   ├── .env               # Змінні оточення для локальної розробки
│   └── .env.example       # Приклад файлу змінних оточення
├── docker/                # Docker конфігурація
│   ├── Dockerfile         # Docker образ для Django
│   └── docker-compose.yml # Оркестрація сервісів
├── venv/                  # Python віртуальне оточення
├── requirements.txt       # Python залежності
└── README.md             # Документація проекту
```

## Технології

- **Python 3.13** - мова програмування
- **Django 6.0** - веб-фреймворк
- **PostgreSQL 16** - база даних
- **Docker & Docker Compose** - контейнеризація

## Швидкий старт

### 1. Повний запуск в Docker (рекомендовано)

```bash
# Клонувати репозиторій
git clone <repository-url>
cd new_whmcs

# Запустити всі сервіси в Docker
cd docker
docker-compose up --build

# Проект буде доступний на http://localhost:8000
```

### 2. Локальна розробка (Django локально + БД в Docker)

```bash
# 1. Запустити тільки PostgreSQL в Docker
cd docker
docker-compose up db

# 2. Активувати віртуальне оточення
source venv/bin/activate

# 3. Встановити залежності (якщо потрібно)
pip install -r requirements.txt

# 4. Перейти в папку Django проекту
cd src

# 5. Виконати міграції
python manage.py migrate

# 6. Створити суперкористувача (опціонально)
python manage.py createsuperuser

# 7. Запустити Django сервер
python manage.py runserver

# Проект буде доступний на http://localhost:8000
```

## Корисні команди

### Docker команди
```bash
# Запустити сервіси
docker-compose up

# Запустити в фоновому режимі
docker-compose up -d

# Перебудувати образи
docker-compose up --build

# Зупинити сервіси
docker-compose down

# Переглянути логи
docker-compose logs web
docker-compose logs db
```

### Django команди
```bash
# Створити міграції
python manage.py makemigrations

# Застосувати міграції
python manage.py migrate

# Створити суперкористувача
python manage.py createsuperuser

# Запустити сервер розробки
python manage.py runserver

# Запустити Django shell
python manage.py shell
```

## Налаштування бази даних

### Параметри підключення до PostgreSQL:
- **Host**: localhost (для локальної розробки) або db (в Docker)
- **Port**: 5432
- **Database**: whmcs_db
- **Username**: whmcs_user
- **Password**: whmcs_password

### Підключення до БД через psql:
```bash
# Якщо PostgreSQL запущений в Docker
docker-compose exec db psql -U whmcs_user -d whmcs_db
```

## Змінні оточення

Скопіюйте `.env.example` в `.env` та налаштуйте змінні під ваші потреби:

```bash
cp src/.env.example src/.env
```

## Розробка

1. Активуйте віртуальне оточення: `source venv/bin/activate`
2. Встановіть нові залежності: `pip install package_name`
3. Оновіть requirements.txt: `pip freeze > requirements.txt`
4. Створіть міграції після змін в моделях: `python manage.py makemigrations`
5. Застосуйте міграції: `python manage.py migrate`
