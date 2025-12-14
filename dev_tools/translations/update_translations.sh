#!/bin/bash

# Скрипт для оновлення перекладів WHMCS Admin Panel
# Використання: ./dev_tools/update_translations.sh [мова]

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для виводу кольорових повідомлень
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка, чи запущено з правильної директорії
if [ ! -f "src/manage.py" ]; then
    print_error "Скрипт повинен запускатися з кореневої директорії проекту!"
    exit 1
fi

# Перевірка віртуального середовища
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Віртуальне середовище не активовано. Активую..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Віртуальне середовище активовано"
    else
        print_error "Віртуальне середовище не знайдено!"
        exit 1
    fi
fi

cd src

# Підтримувані мови
SUPPORTED_LANGUAGES=("en" "uk")

# Якщо передано параметр мови
if [ ! -z "$1" ]; then
    LANGUAGE="$1"
    # Перевірка, чи підтримується мова
    if [[ ! " ${SUPPORTED_LANGUAGES[@]} " =~ " ${LANGUAGE} " ]]; then
        print_error "Мова '$LANGUAGE' не підтримується!"
        print_info "Підтримувані мови: ${SUPPORTED_LANGUAGES[*]}"
        exit 1
    fi
    LANGUAGES_TO_UPDATE=("$LANGUAGE")
else
    LANGUAGES_TO_UPDATE=("${SUPPORTED_LANGUAGES[@]}")
fi

print_info "Початок оновлення перекладів..."

# Оновлення перекладів для кожної мови
for lang in "${LANGUAGES_TO_UPDATE[@]}"; do
    print_info "Обробка мови: $lang"
    
    # Створення/оновлення файлів перекладів
    print_info "Генерація файлів перекладів для $lang..."
    python manage.py makemessages -l "$lang" --ignore=venv
    
    if [ $? -eq 0 ]; then
        print_success "Файли перекладів для $lang згенеровано"
    else
        print_error "Помилка при генерації файлів перекладів для $lang"
        exit 1
    fi
done

# Компіляція всіх перекладів
print_info "Компіляція перекладів..."
python manage.py compilemessages

if [ $? -eq 0 ]; then
    print_success "Переклади скомпільовано успішно"
else
    print_error "Помилка при компіляції перекладів"
    exit 1
fi

# Статистика перекладів
print_info "Статистика перекладів:"
for lang in "${SUPPORTED_LANGUAGES[@]}"; do
    if [ -f "locale/$lang/LC_MESSAGES/django.po" ]; then
        total=$(grep -c "^msgid " "locale/$lang/LC_MESSAGES/django.po" 2>/dev/null | head -1)
        translated=$(grep -c "^msgstr \"[^\"]\+" "locale/$lang/LC_MESSAGES/django.po" 2>/dev/null | head -1)
        
        # Встановлення значень за замовчуванням
        total=${total:-0}
        translated=${translated:-0}
        
        if [ "$total" -gt 1 ]; then
            # Віднімаємо 1, бо перший msgid "" не рахується
            real_total=$((total - 1))
            if [ "$real_total" -gt 0 ]; then
                percentage=$((translated * 100 / real_total))
                print_info "$lang: $translated/$real_total перекладено ($percentage%)"
            else
                print_info "$lang: немає рядків для перекладу"
            fi
        else
            print_info "$lang: файл перекладів порожній або пошкоджений"
        fi
    fi
done

print_success "Оновлення перекладів завершено!"
print_info "Не забудьте перезапустити сервер розробки для застосування змін"

cd ..