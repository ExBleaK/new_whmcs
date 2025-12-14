# Docker Configuration для WHMCS Admin Panel

## Файли конфігурації

### Dockerfile
Єдиний універсальний Dockerfile з підтримкою різних режимів збірки.

**Build Arguments:**
- `BUILD_MODE` - режим збірки (`development` або `production`)
- `ENABLE_HEALTHCHECK` - увімкнути health check (`true` або `false`)

**Особливості:**
- Встановлює `gettext` для роботи з перекладами
- Автоматично валідує та компілює переклади під час збірки
- Умовна збірка залежно від режиму:
  - **Development**: швидка збірка, root користувач
  - **Production**: збір статичних файлів, gosu для безпеки, health check

### docker-compose.yml
Конфігурація для розробки та продакшн середовищ.

**Сервіси:**
- `db` - PostgreSQL база даних
- `web` - Django додаток (розробка, `BUILD_MODE=development`)
- `web-prod` - Django додаток (продакшн, `BUILD_MODE=production`, профіль `production`)

### entrypoint.sh
Універсальний entrypoint скрипт для різних режимів запуску.

**Функції:**
- Автоматичне визначення режиму (development/production)
- Перемикання на непривілейованого користувача в продакшн
- Автоматичні міграції бази даних
- Створення адмін користувача (тільки в розробці)
- Перекомпіляція перекладів при потребі

### check_translations.sh
Скрипт для валідації та компіляції перекладів в Docker контейнері.

**Функції:**
- Перевірка наявності gettext
- Валідація синтаксису .po файлів
- Статистика перекладів
- Компіляція в .mo файли
- Детальне логування процесу

## Використання

### Розробка

```bash
# Запуск розробницького середовища
make dev

# Збірка та запуск
make dev-build

# Перегляд логів
make logs
```

### Продакшн

```bash
# Запуск продакшн середовища
make prod

# Збірка та запуск продакшн
make prod-build
```

### Ручне управління Docker

```bash
# Розробка
docker-compose -f docker/docker-compose.yml up --build

# Продакшн
docker-compose -f docker/docker-compose.yml --profile production up --build web-prod

# Прямі збірки
docker build -f docker/Dockerfile --build-arg BUILD_MODE=development -t whmcs-admin:dev .
docker build -f docker/Dockerfile --build-arg BUILD_MODE=production --build-arg ENABLE_HEALTHCHECK=true -t whmcs-admin:prod .
```

## Процес збірки з перекладами

### 1. Встановлення залежностей
```dockerfile
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*
```

### 2. Копіювання проекту
```dockerfile
COPY src/ .
```

### 3. Валідація та компіляція перекладів
```dockerfile
COPY docker/check_translations.sh /tmp/check_translations.sh
RUN chmod +x /tmp/check_translations.sh
RUN /tmp/check_translations.sh && rm /tmp/check_translations.sh
```

**Примітка:** Для розробки використовується новий Python скрипт `dev_tools/translations.py`, але в Docker збірці залишається bash скрипт для простоти та надійності контейнера.

### Що відбувається під час валідації:

1. **Пошук файлів перекладів** - знаходить всі .po файли
2. **Валідація синтаксису** - перевіряє кожен файл з `msgfmt --check-format`
3. **Статистика** - показує відсоток перекладених рядків
4. **Компіляція** - створює .mo файли з `python manage.py compilemessages`
5. **Перевірка результату** - підтверджує створення .mo файлів

### Приклад виводу під час збірки:

```
=== WHMCS Translation Validation ===
[SUCCESS] gettext знайдено
[INFO] Пошук файлів перекладів...
[SUCCESS] Знайдено файли перекладів:
  - locale/en/LC_MESSAGES/django.po
  - locale/uk/LC_MESSAGES/django.po
[INFO] Валідація файлів перекладів...
[INFO] Перевірка: locale/en/LC_MESSAGES/django.po
[SUCCESS] ✓ Синтаксис правильний: locale/en/LC_MESSAGES/django.po
  [INFO] Статистика: 0/45 перекладено (0%)
[INFO] Перевірка: locale/uk/LC_MESSAGES/django.po
[SUCCESS] ✓ Синтаксис правильний: locale/uk/LC_MESSAGES/django.po
  [INFO] Статистика: 44/45 перекладено (97%)
[INFO] Компіляція перекладів...
[SUCCESS] Переклади успішно скомпільовано
[SUCCESS] Скомпільовані файли:
  - locale/en/LC_MESSAGES/django.mo (1234 bytes)
  - locale/uk/LC_MESSAGES/django.mo (5678 bytes)
[SUCCESS] Валідація перекладів завершена успішно!
```

## Інтеграція з dev_tools

### Розробка поза Docker
Для розробки поза Docker використовуйте новий Python скрипт:

```bash
# Оновити переклади локально
python dev_tools/translations.py update

# Перевірити якість
python dev_tools/translations.py test

# Показати статистику
python dev_tools/translations.py stats
```

### Синхронізація з Docker
Після оновлення перекладів локально, перебудуйте контейнер:

```bash
# Оновити переклади
make translations

# Перебудувати контейнер
make dev-build
```

## Налагодження

### Перевірка перекладів в контейнері
```bash
# Запуск контейнера з shell
docker run --rm -it whmcs-admin:test /bin/bash

# Перевірка файлів перекладів
find locale -name "*.po" -o -name "*.mo"

# Ручна компіляція
python manage.py compilemessages --verbosity=2
```

### Перевірка логів збірки
```bash
# Збірка з детальними логами
docker build -f docker/Dockerfile --progress=plain -t whmcs-admin .
```

## Оптимізація

### Multi-stage build (майбутнє покращення)
Можна оптимізувати Dockerfile використовуючи multi-stage build для зменшення розміру образу:

```dockerfile
# Build stage
FROM python:3.13-slim as builder
# ... встановлення залежностей та компіляція

# Runtime stage  
FROM python:3.13-slim as runtime
# ... копіювання тільки необхідних файлів
```

### Кешування перекладів
Переклади компілюються тільки при зміні .po файлів завдяки Docker layer caching.