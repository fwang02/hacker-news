import os
import django
from django.conf import settings

# Establece la configuración de Django usando el fichero settings.py
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hacker_news.settings")

# Inicializa Django
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def generate_tokens_for_existing_users():
    users = User.objects.all()
    for user in users:
        token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"Generated token for {user.username}: {token.key}")
        else:
            print(f"Token already exists for {user.username}: {token.key}")

# Run the function to generate tokens for existing users
generate_tokens_for_existing_users()
