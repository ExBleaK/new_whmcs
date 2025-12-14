#!/bin/bash

# Скрипт для автоматичного заповнення англійських перекладів
# Для англійської мови msgstr повинен дорівнювати msgid

set -e

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

# Перевірка, чи запущено з правильної директорії
if [ ! -f "src/manage.py" ]; then
    print_error "Скрипт повинен запускатися з кореневої директорії проекту!"
    exit 1
fi

EN_PO_FILE="src/locale/en/LC_MESSAGES/django.po"

if [ ! -f "$EN_PO_FILE" ]; then
    print_error "Англійський файл перекладів не знайдено: $EN_PO_FILE"
    exit 1
fi

print_info "Виправлення англійських перекладів..."

# Використовуємо Python для обробки файлу
python3 << 'EOF'
import re

# Читаємо файл
with open('src/locale/en/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Замінюємо порожні msgstr на відповідні msgid
# Паттерн: msgid "text" \n msgstr ""
pattern = r'msgid "([^"]+)"\nmsgstr ""'

def replace_func(match):
    msgid_text = match.group(1)
    return f'msgid "{msgid_text}"\nmsgstr "{msgid_text}"'

# Виконуємо заміну
new_content = re.sub(pattern, replace_func, content)

# Записуємо результат
with open('src/locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("English translations fixed successfully!")
EOF

print_success "Англійські переклади виправлено"

# Компілюємо переклади
print_info "Компіляція перекладів..."
cd src
python manage.py compilemessages
cd ..

print_success "Переклади скомпільовано"
print_info "Перезапустіть сервер для застосування змін"