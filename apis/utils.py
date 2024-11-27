from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed


def get_user_from_api_key(api_key):
    """
    Función que recibe una API Key y devuelve el usuario correspondiente.
    Si la API Key no es válida o no existe, devuelve None.
    """
    if not api_key:
        return None

    try:
        user = User.objects.get(profile__api_key=api_key)  # Asumimos que la API Key está asociada al perfil del usuario
        return user
    except User.DoesNotExist:
        return None

