#!/bin/bash

# Скрипт для перевірки перекладів в Docker контейнері
# Використовується під час збірки для валідації

set -e

echo "=== WHMCS Translation Validation ==="

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Перевірка наявності gettext
if ! command -v msgfmt &> /dev/null; then
    print_error "gettext не встановлено! Встановіть пакет gettext."
    exit 1
fi

print_success "gettext знайдено"

# Пошук файлів перекладів
print_info "Пошук файлів перекладів..."
po_files=$(find locale -name "*.po" -type f 2>/dev/null || true)

if [ -z "$po_files" ]; then
    print_warning "Файли перекладів не знайдено"
    exit 0
fi

print_success "Знайдено файли перекладів:"
echo "$po_files" | while read -r file; do
    echo "  - $file"
done

# Валідація кожного файлу
print_info "Валідація файлів перекладів..."
validation_failed=false

echo "$po_files" | while read -r po_file; do
    print_info "Перевірка: $po_file"
    
    # Перевірка синтаксису
    if msgfmt --check-format "$po_file" 2>/dev/null; then
        print_success "✓ Синтаксис правильний: $po_file"
    else
        print_error "✗ Помилка синтаксису: $po_file"
        validation_failed=true
    fi
    
    # Статистика перекладів
    if [ -f "$po_file" ]; then
        total=$(grep -c "^msgid " "$po_file" 2>/dev/null | head -1)
        translated=$(grep -c "^msgstr \"[^\"]\+" "$po_file" 2>/dev/null | head -1)
        
        # Встановлення значень за замовчуванням
        total=${total:-0}
        translated=${translated:-0}
        
        if [ "$total" -gt 1 ] && [ "$translated" -ge 0 ]; then
            real_total=$((total - 1))  # Віднімаємо перший порожній msgid
            if [ "$real_total" -gt 0 ]; then
                percentage=$((translated * 100 / real_total))
                print_info "  Статистика: $translated/$real_total перекладено ($percentage%)"
                
                if [ "$percentage" -lt 50 ]; then
                    print_warning "  Низький відсоток перекладів: $percentage%"
                fi
            else
                print_info "  Немає рядків для перекладу"
            fi
        else
            print_info "  Файл перекладів порожній або має тільки заголовок"
        fi
    fi
done

# Компіляція перекладів
print_info "Компіляція перекладів..."
if python manage.py compilemessages --verbosity=1; then
    print_success "Переклади успішно скомпільовано"
else
    print_error "Помилка компіляції перекладів"
    exit 1
fi

# Перевірка скомпільованих файлів
print_info "Перевірка скомпільованих файлів..."
mo_files=$(find locale -name "*.mo" -type f 2>/dev/null || true)

if [ -z "$mo_files" ]; then
    print_error "Скомпільовані файли не знайдено!"
    exit 1
fi

print_success "Скомпільовані файли:"
echo "$mo_files" | while read -r file; do
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
    echo "  - $file ($size bytes)"
done

print_success "Валідація перекладів завершена успішно!"