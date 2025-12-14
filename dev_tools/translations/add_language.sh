#!/bin/bash

# Скрипт для додавання нової мови до WHMCS Admin Panel
# Використання: ./dev_tools/add_language.sh <код_мови> <назва_мови>

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка параметрів
if [ $# -ne 2 ]; then
    print_error "Використання: $0 <код_мови> <назва_мови>"
    print_info "Приклад: $0 de Deutsch"
    exit 1
fi

LANG_CODE="$1"
LANG_NAME="$2"

# Перевірка, чи запущено з правильної директорії
if [ ! -f "src/manage.py" ]; then
    print_error "Скрипт повинен запускатися з кореневої директорії проекту!"
    exit 1
fi

print_info "Додавання мови: $LANG_NAME ($LANG_CODE)"

# Перевірка віртуального середовища
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
fi

cd src

# Створення директорії для мови
print_info "Створення директорії для мови..."
mkdir -p "locale/$LANG_CODE/LC_MESSAGES"

# Генерація файлів перекладів
print_info "Генерація файлів перекладів..."
python manage.py makemessages -l "$LANG_CODE" --ignore=venv

if [ $? -eq 0 ]; then
    print_success "Файли перекладів створено"
else
    print_error "Помилка при створенні файлів перекладів"
    exit 1
fi

# Додавання мови в settings.py
print_info "Оновлення налаштувань..."
SETTINGS_FILE="whmcs_project/settings.py"

# Перевірка, чи мова вже додана
if grep -q "('$LANG_CODE'" "$SETTINGS_FILE"; then
    print_info "Мова $LANG_CODE вже присутня в налаштуваннях"
else
    # Додавання мови в LANGUAGES
    sed -i.bak "/('uk', 'Українська'),/a\\
    ('$LANG_CODE', '$LANG_NAME'),
" "$SETTINGS_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Мову додано в налаштування"
        rm "$SETTINGS_FILE.bak" 2>/dev/null || true
    else
        print_error "Помилка при оновленні налаштувань"
        exit 1
    fi
fi

print_success "Мова $LANG_NAME ($LANG_CODE) успішно додана!"
print_info "Тепер ви можете:"
print_info "1. Відредагувати файл src/locale/$LANG_CODE/LC_MESSAGES/django.po"
print_info "2. Запустити ./dev_tools/update_translations.sh для компіляції"
print_info "3. Перезапустити сервер розробки"

cd ..