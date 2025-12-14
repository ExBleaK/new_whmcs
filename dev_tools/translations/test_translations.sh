#!/bin/bash

# Скрипт для тестування перекладів
# Перевіряє, чи всі тексти мають переклади

set -e

# Кольори
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

# Перевірка директорії
if [ ! -f "src/manage.py" ]; then
    print_error "Скрипт повинен запускатися з кореневої директорії проекту!"
    exit 1
fi

cd src

print_info "Перевірка перекладів..."

# Підтримувані мови
LANGUAGES=("en" "uk")

for lang in "${LANGUAGES[@]}"; do
    po_file="locale/$lang/LC_MESSAGES/django.po"
    
    if [ ! -f "$po_file" ]; then
        print_error "Файл перекладів для $lang не знайдено: $po_file"
        continue
    fi
    
    print_info "Перевірка мови: $lang"
    
    # Підрахунок загальної кількості рядків
    total=$(grep -c "^msgid " "$po_file" 2>/dev/null || echo "0")
    
    # Підрахунок перекладених рядків (не порожні msgstr)
    translated=$(grep -c "^msgstr \"[^\"]\+\"" "$po_file" 2>/dev/null || echo "0")
    
    # Підрахунок порожніх перекладів
    empty=$(grep -c "^msgstr \"\"$" "$po_file" 2>/dev/null || echo "0")
    
    # Підрахунок fuzzy перекладів
    fuzzy=$(grep -c "#, fuzzy" "$po_file" 2>/dev/null || echo "0")
    
    # Перевірка на валідність чисел
    [ "$total" = "" ] && total=0
    [ "$translated" = "" ] && translated=0
    [ "$empty" = "" ] && empty=0
    [ "$fuzzy" = "" ] && fuzzy=0
    
    if [ "$total" -gt 0 ] && [ "$translated" -ge 0 ] && [ "$total" != "" ] && [ "$translated" != "" ]; then
        percentage=$((translated * 100 / total))
        
        echo "  Загально: $total"
        echo "  Перекладено: $translated ($percentage%)"
        echo "  Порожніх: $empty"
        echo "  Fuzzy: $fuzzy"
        
        if [ "$percentage" -eq 100 ] && [ "$fuzzy" -eq 0 ]; then
            print_success "Мова $lang: всі переклади готові"
        elif [ "$percentage" -ge 80 ]; then
            print_warning "Мова $lang: переклади майже готові"
        else
            print_warning "Мова $lang: потребує доопрацювання"
        fi
        
        # Показати перші 5 непереведених рядків
        if [ "$empty" -gt 0 ]; then
            print_info "Перші непереведені рядки для $lang:"
            grep -B1 "^msgstr \"\"$" "$po_file" | grep "^msgid " | head -5 | sed 's/^msgid /  - /'
        fi
        
        # Показати fuzzy переклади
        if [ "$fuzzy" -gt 0 ]; then
            print_warning "Fuzzy переклади для $lang (потребують перевірки):"
            grep -A2 "#, fuzzy" "$po_file" | grep "^msgid " | head -3 | sed 's/^msgid /  - /'
        fi
    else
        print_error "Файл перекладів для $lang порожній або пошкоджений"
    fi
    
    echo ""
done

# Перевірка компільованих файлів
print_info "Перевірка скомпільованих файлів..."
for lang in "${LANGUAGES[@]}"; do
    mo_file="locale/$lang/LC_MESSAGES/django.mo"
    po_file="locale/$lang/LC_MESSAGES/django.po"
    
    if [ -f "$mo_file" ]; then
        if [ "$po_file" -nt "$mo_file" ]; then
            print_warning "Файл $po_file новіший за $mo_file - потрібна перекомпіляція"
        else
            print_success "Файл $mo_file актуальний"
        fi
    else
        print_error "Скомпільований файл $mo_file не знайдено"
    fi
done

print_info "Перевірка завершена"

cd ..