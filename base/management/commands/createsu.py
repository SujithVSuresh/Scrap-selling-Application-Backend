# images/management/commands/createsu.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='ajith').exists():
            User.objects.create_superuser(
                username='ajith',
                password='ajith@123'
            )
        print('Superuser has been created.')
