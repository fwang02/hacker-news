# users/signals.py
import logging
from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def create_profile_on_login(sender, request, user, **kwargs):
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        logger.info(f'Profile created for user: {user.username}')
    else:
        logger.info(f'Profile already exists for user: {user.username}')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created or instance.is_superuser:
        Profile.objects.get_or_create(user=instance)