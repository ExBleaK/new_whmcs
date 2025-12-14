#!/usr/bin/env python3
"""
WHMCS Admin Panel - Translation Management Tool

Unified Python script for managing translations with multiple commands.
Replaces all bash scripts in dev_tools/translations/ directory.

Usage:
    python dev_tools/translations.py <command> [options]

Commands:
    update [lang]     - Update and compile translations
    test             - Test translation quality  
    fix-english      - Fix English translations (msgstr = msgid)
    add <code> <name> - Add new language support
    stats            - Show translation statistics
    help             - Show this help message

Examples:
    python dev_tools/translations.py update
    python dev_tools/translations.py update uk
    python dev_tools/translations.py test
    python dev_tools/translations.py add de Deutsch
    python dev_tools/translations.py fix-english
"""

import argparse
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_info(message: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message: str) -> None:
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str) -> None:
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str) -> None:
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

class TranslationManager:
    """Main class for managing translations"""
    
    SUPPORTED_LANGUAGES = ['en', 'uk']
    PROJECT_ROOT = Path(__file__).parent.parent
    SRC_DIR = PROJECT_ROOT / 'src'
    LOCALE_DIR = SRC_DIR / 'locale'
    
    def __init__(self):
        self.check_environment()
    
    def check_environment(self) -> None:
        """Check if we're in the right directory and environment"""
        if not (self.SRC_DIR / 'manage.py').exists():
            print_error("Script must be run from project root directory!")
            print_error(f"Expected manage.py at: {self.SRC_DIR / 'manage.py'}")
            sys.exit(1)
    
    def run_django_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Run Django management command"""
        if cwd is None:
            cwd = self.SRC_DIR
            
        try:
            result = subprocess.run(
                ['python', 'manage.py'] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def get_translation_stats(self, lang: str) -> Dict[str, int]:
        """Get translation statistics for a language"""
        po_file = self.LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'
        
        if not po_file.exists():
            return {'total': 0, 'translated': 0, 'empty': 0, 'fuzzy': 0}
        
        try:
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count different types of entries
            total = len(re.findall(r'^msgid "([^"]*)"$', content, re.MULTILINE))
            translated = len(re.findall(r'^msgstr "([^"]+)"$', content, re.MULTILINE))
            empty = len(re.findall(r'^msgstr ""$', content, re.MULTILINE))
            fuzzy = len(re.findall(r'^#, fuzzy', content, re.MULTILINE))
            
            # Subtract header msgid ""
            if total > 0:
                total -= 1
                
            return {
                'total': total,
                'translated': translated,
                'empty': empty,
                'fuzzy': fuzzy
            }
        except Exception as e:
            print_error(f"Error reading {po_file}: {e}")
            return {'total': 0, 'translated': 0, 'empty': 0, 'fuzzy': 0}
    
    def update_translations(self, languages: Optional[List[str]] = None) -> bool:
        """Update and compile translations"""
        if languages is None:
            languages = self.SUPPORTED_LANGUAGES
        
        # Validate languages
        for lang in languages:
            if lang not in self.SUPPORTED_LANGUAGES:
                print_error(f"Language '{lang}' not supported!")
                print_info(f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES)}")
                return False
        
        print_info("Starting translation update...")
        
        # Generate translation files for each language
        for lang in languages:
            print_info(f"Processing language: {lang}")
            
            print_info(f"Generating translation files for {lang}...")
            success, output = self.run_django_command(['makemessages', '-l', lang, '--ignore=venv'])
            
            if success:
                print_success(f"Translation files for {lang} generated")
            else:
                print_error(f"Error generating translation files for {lang}")
                print_error(output)
                return False
        
        # Compile all translations
        print_info("Compiling translations...")
        success, output = self.run_django_command(['compilemessages'])
        
        if success:
            print_success("Translations compiled successfully")
        else:
            print_error("Error compiling translations")
            print_error(output)
            return False
        
        # Show statistics
        print_info("Translation statistics:")
        for lang in self.SUPPORTED_LANGUAGES:
            stats = self.get_translation_stats(lang)
            if stats['total'] > 0:
                percentage = (stats['translated'] * 100) // stats['total']
                print_info(f"{lang}: {stats['translated']}/{stats['total']} translated ({percentage}%)")
            else:
                print_info(f"{lang}: no translation file or empty")
        
        print_success("Translation update completed!")
        print_info("Restart development server to apply changes")
        return True
    
    def test_translations(self) -> bool:
        """Test translation quality and show detailed statistics"""
        print_info("Checking translations...")
        
        for lang in self.SUPPORTED_LANGUAGES:
            po_file = self.LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'
            mo_file = self.LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.mo'
            
            if not po_file.exists():
                print_error(f"Translation file for {lang} not found: {po_file}")
                continue
            
            print_info(f"Checking language: {lang}")
            
            stats = self.get_translation_stats(lang)
            
            if stats['total'] > 0:
                percentage = (stats['translated'] * 100) // stats['total']
                
                print(f"  Total: {stats['total']}")
                print(f"  Translated: {stats['translated']} ({percentage}%)")
                print(f"  Empty: {stats['empty']}")
                print(f"  Fuzzy: {stats['fuzzy']}")
                
                if percentage == 100 and stats['fuzzy'] == 0:
                    print_success(f"Language {lang}: all translations ready")
                elif percentage >= 80:
                    print_warning(f"Language {lang}: translations almost ready")
                else:
                    print_warning(f"Language {lang}: needs more work")
                
                # Show first few untranslated strings
                if stats['empty'] > 0:
                    print_info(f"First untranslated strings for {lang}:")
                    try:
                        with open(po_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find empty msgstr entries
                        pattern = r'msgid "([^"]+)"\nmsgstr ""'
                        matches = re.findall(pattern, content)
                        for i, match in enumerate(matches[:5]):
                            print(f"  - {match}")
                    except Exception as e:
                        print_error(f"Error reading untranslated strings: {e}")
                
                # Show fuzzy translations
                if stats['fuzzy'] > 0:
                    print_warning(f"Fuzzy translations for {lang} (need review):")
                    try:
                        with open(po_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        fuzzy_count = 0
                        for i, line in enumerate(lines):
                            if '#, fuzzy' in line and fuzzy_count < 3:
                                # Find the next msgid
                                for j in range(i + 1, min(i + 5, len(lines))):
                                    if lines[j].startswith('msgid "'):
                                        msgid = lines[j].strip()[7:-1]  # Remove msgid " and "
                                        print(f"  - {msgid}")
                                        fuzzy_count += 1
                                        break
                    except Exception as e:
                        print_error(f"Error reading fuzzy translations: {e}")
            else:
                print_error(f"Translation file for {lang} is empty or corrupted")
            
            # Check compiled files
            if mo_file.exists():
                if po_file.stat().st_mtime > mo_file.stat().st_mtime:
                    print_warning(f"File {po_file.name} is newer than {mo_file.name} - recompilation needed")
                else:
                    print_success(f"File {mo_file.name} is up to date")
            else:
                print_error(f"Compiled file {mo_file} not found")
            
            print()
        
        print_info("Translation check completed")
        return True
    
    def fix_english_translations(self) -> bool:
        """Fix English translations by setting msgstr = msgid"""
        en_po_file = self.LOCALE_DIR / 'en' / 'LC_MESSAGES' / 'django.po'
        
        if not en_po_file.exists():
            print_error(f"English translation file not found: {en_po_file}")
            return False
        
        print_info("Fixing English translations...")
        
        try:
            with open(en_po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace empty msgstr with corresponding msgid
            pattern = r'msgid "([^"]+)"\nmsgstr ""'
            
            def replace_func(match):
                msgid_text = match.group(1)
                return f'msgid "{msgid_text}"\nmsgstr "{msgid_text}"'
            
            new_content = re.sub(pattern, replace_func, content)
            
            with open(en_po_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print_success("English translations fixed")
            
            # Compile translations
            print_info("Compiling translations...")
            success, output = self.run_django_command(['compilemessages'])
            
            if success:
                print_success("Translations compiled")
            else:
                print_error("Error compiling translations")
                print_error(output)
                return False
            
            print_info("Restart development server to apply changes")
            return True
            
        except Exception as e:
            print_error(f"Error fixing English translations: {e}")
            return False
    
    def add_language(self, lang_code: str, lang_name: str) -> bool:
        """Add support for a new language"""
        print_info(f"Adding language: {lang_name} ({lang_code})")
        
        # Create directory for language
        lang_dir = self.LOCALE_DIR / lang_code / 'LC_MESSAGES'
        lang_dir.mkdir(parents=True, exist_ok=True)
        print_info("Language directory created")
        
        # Generate translation files
        print_info("Generating translation files...")
        success, output = self.run_django_command(['makemessages', '-l', lang_code, '--ignore=venv'])
        
        if not success:
            print_error("Error generating translation files")
            print_error(output)
            return False
        
        print_success("Translation files created")
        
        # Update settings.py
        settings_file = self.SRC_DIR / 'whmcs_project' / 'settings.py'
        print_info("Updating settings...")
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if language already exists
            if f"('{lang_code}'" in content:
                print_info(f"Language {lang_code} already present in settings")
            else:
                # Add language to LANGUAGES
                pattern = r"(\('uk', 'Українська'\),)"
                replacement = f"\\1\n    ('{lang_code}', '{lang_name}'),"
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    with open(settings_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print_success("Language added to settings")
                else:
                    print_error("Could not update settings automatically")
                    return False
        
        except Exception as e:
            print_error(f"Error updating settings: {e}")
            return False
        
        print_success(f"Language {lang_name} ({lang_code}) successfully added!")
        print_info("Now you can:")
        print_info(f"1. Edit file src/locale/{lang_code}/LC_MESSAGES/django.po")
        print_info("2. Run: python dev_tools/translations.py update")
        print_info("3. Restart development server")
        
        return True
    
    def show_stats(self) -> bool:
        """Show detailed translation statistics"""
        print_info("Translation Statistics")
        print("=" * 50)
        
        for lang in self.SUPPORTED_LANGUAGES:
            stats = self.get_translation_stats(lang)
            
            if stats['total'] > 0:
                percentage = (stats['translated'] * 100) // stats['total']
                
                print(f"\n{lang.upper()} ({self.get_language_name(lang)}):")
                print(f"  Total strings: {stats['total']}")
                print(f"  Translated: {stats['translated']} ({percentage}%)")
                print(f"  Empty: {stats['empty']}")
                print(f"  Fuzzy: {stats['fuzzy']}")
                
                # Progress bar
                bar_length = 30
                filled = int(bar_length * percentage / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"  Progress: [{bar}] {percentage}%")
            else:
                print(f"\n{lang.upper()}: No translation file found")
        
        return True
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name by code"""
        names = {
            'en': 'English',
            'uk': 'Українська'
        }
        return names.get(lang_code, lang_code)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='WHMCS Admin Panel Translation Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update and compile translations')
    update_parser.add_argument('language', nargs='?', help='Specific language to update (optional)')
    
    # Test command
    subparsers.add_parser('test', help='Test translation quality')
    
    # Fix English command
    subparsers.add_parser('fix-english', help='Fix English translations (msgstr = msgid)')
    
    # Add language command
    add_parser = subparsers.add_parser('add', help='Add new language support')
    add_parser.add_argument('code', help='Language code (e.g., de, fr)')
    add_parser.add_argument('name', help='Language name (e.g., Deutsch, Français)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show translation statistics')
    
    # Help command
    subparsers.add_parser('help', help='Show help message')
    
    args = parser.parse_args()
    
    if not args.command or args.command == 'help':
        parser.print_help()
        return 0
    
    manager = TranslationManager()
    
    try:
        if args.command == 'update':
            languages = [args.language] if args.language else None
            success = manager.update_translations(languages)
        elif args.command == 'test':
            success = manager.test_translations()
        elif args.command == 'fix-english':
            success = manager.fix_english_translations()
        elif args.command == 'add':
            success = manager.add_language(args.code, args.name)
        elif args.command == 'stats':
            success = manager.show_stats()
        else:
            print_error(f"Unknown command: {args.command}")
            parser.print_help()
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())