from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    karma = models.IntegerField(default=0)  # Campo para el karma
    about = models.TextField(blank=True)    # Campo para la descripción

    def __str__(self):
        return f"{self.user.username}'s profile"
