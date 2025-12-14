from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config


class Command(BaseCommand):
    help = 'Створює адміністратора з налаштувань .env'

    def handle(self, *args, **options):
        username = config('ADMIN_USERNAME', default='admin')
        password = config('ADMIN_PASSWORD', default='admin123')
        email = config('ADMIN_EMAIL', default='admin@whmcs.local')

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Користувач "{username}" вже існує')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Адміністратор створений успішно:\n'
                f'Логін: {username}\n'
                f'Email: {email}\n'
                f'Пароль: {password}'
            )
        )