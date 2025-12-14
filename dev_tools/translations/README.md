# Translation Tools для WHMCS Admin Panel

Ця папка містить інструменти для роботи з перекладами та інтернаціоналізацією.

## Скрипти

### 1. update_translations.sh
**Призначення:** Оновлює та компілює переклади для всіх або конкретної мови.

**Використання:**
```bash
# Оновити всі мови
./dev_tools/translations/update_translations.sh

# Оновити конкретну мову
./dev_tools/translations/update_translations.sh uk
./dev_tools/translations/update_translations.sh en
```

**Що робить:**
- Генерує файли .po для вказаних мов
- Компілює переклади в .mo файли
- Показує статистику перекладів
- Перевіряє віртуальне середовище
- Автоматично активує venv якщо потрібно

**Вивід:**
```
[INFO] Початок оновлення перекладів...
[INFO] Обробка мови: uk
[SUCCESS] Файли перекладів для uk згенеровано
[SUCCESS] Переклади скомпільовано успішно
[INFO] Статистика перекладів:
[INFO] en: 0/45 перекладено (0%)
[INFO] uk: 44/45 перекладено (97%)
```

### 2. add_language.sh
**Призначення:** Додає підтримку нової мови до проекту.

**Використання:**
```bash
./dev_tools/translations/add_language.sh <код_мови> <назва_мови>

# Приклади:
./dev_tools/translations/add_language.sh de Deutsch
./dev_tools/translations/add_language.sh fr Français
./dev_tools/translations/add_language.sh pl Polski
```

**Що робить:**
- Створює директорію для нової мови
- Генерує початковий файл перекладів
- Додає мову в settings.py
- Надає інструкції для подальших дій

### 3. test_translations.sh
**Призначення:** Перевіряє стан перекладів та виявляє проблеми.

**Використання:**
```bash
./dev_tools/translations/test_translations.sh
```

**Що робить:**
- Показує статистику перекладів для всіх мов
- Виявляє непереведені рядки
- Знаходить fuzzy переклади (потребують перевірки)
- Перевіряє актуальність скомпільованих файлів

**Вивід:**
```
[INFO] Перевірка мови: uk
  Загально: 46
  Перекладено: 44 (95%)
  Порожніх: 2
  Fuzzy: 0
[WARNING] Мова uk: переклади майже готові
```

## Робочий процес

### Додавання нового тексту для перекладу:
1. Додайте `{% trans "Your text" %}` в шаблон
2. Запустіть `./dev_tools/translations/update_translations.sh`
3. Відредагуйте файли `src/locale/*/LC_MESSAGES/django.po`
4. Знову запустіть `./dev_tools/translations/update_translations.sh`
5. Перезапустіть сервер

### Додавання нової мови:
1. Запустіть `./dev_tools/translations/add_language.sh код назва`
2. Відредагуйте `src/locale/код/LC_MESSAGES/django.po`
3. Запустіть `./dev_tools/translations/update_translations.sh`
4. Перезапустіть сервер

### Перевірка якості перекладів:
1. Запустіть `./dev_tools/translations/test_translations.sh`
2. Виправте знайдені проблеми
3. Перекомпілюйте `./dev_tools/translations/update_translations.sh`

## Підтримувані мови

- **en** (English) - мова за замовчуванням
- **uk** (Українська) - повний переклад

## Структура файлів перекладів

```
src/locale/
├── en/
│   └── LC_MESSAGES/
│       ├── django.po    # Вихідний файл перекладів
│       └── django.mo    # Скомпільований файл
└── uk/
    └── LC_MESSAGES/
        ├── django.po    # Український переклад
        └── django.mo    # Скомпільований файл
```

## JavaScript рішення для перемикання мов

### Проблема з URL префіксами
Django i18n_patterns створює URL з мовними префіксами, але для мови за замовчуванням (англійська) префікс не додається при `prefix_default_language=False`.

### Рішення
Використовується JavaScript для динамічного формування правильного URL перед відправкою форми перемикання мови:

```javascript
// Видаляємо існуючий мовний префікс
const langPrefixes = ['/uk/', '/en/'];
langPrefixes.forEach(function(prefix) {
    if (currentPath.startsWith(prefix)) {
        currentPath = currentPath.substring(prefix.length - 1);
    }
});

// Додаємо новий префікс (крім англійської)
if (langCode === 'en') {
    newPath = currentPath;  // Без префікса
} else {
    newPath = '/' + langCode + currentPath;  // З префіксом
}
```

## Технічні деталі

### Формат файлів .po
```po
#: admin_panel/templates/admin_panel/base.html:20
msgid "Dashboard"
msgstr "Панель управління"
```

- `msgid` - оригінальний текст (зазвичай англійський)
- `msgstr` - переклад
- `#:` - коментар з місцем використання

### Fuzzy переклади
Позначаються як `#, fuzzy` - це переклади, які Django вгадав автоматично і потребують перевірки.

### Компіляція
Файли .po компілюються в бінарні .mo файли для швидкого доступу Django.

## Інтеграція з Docker

Переклади автоматично компілюються під час збірки Docker контейнера через скрипт `docker/check_translations.sh`.

## Налагодження

### Перевірка синтаксису вручну:
```bash
msgfmt --check-format src/locale/uk/LC_MESSAGES/django.po
```

### Ручна компіляція:
```bash
cd src
python manage.py compilemessages --verbosity=2
```

### Пошук непереведених рядків:
```bash
grep -n "msgstr \"\"$" src/locale/uk/LC_MESSAGES/django.po
```