from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Create demo user and print token (username: demo, password: demo)'

    def handle(self, *args, **options):
        username = 'demo'
        password = 'demo'
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING('User "demo" already exists'))
        else:
            user = User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS('Created user "demo"'))

        token, created = Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(f'Token: {token.key}'))
        self.stdout.write(self.style.SUCCESS(f'Credentials -> username: {username}, password: {password}'))