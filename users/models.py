from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    karma = models.IntegerField(default=0)
    about = models.TextField(blank=True, null=True)  # Add this line

    def __str__(self):
        return self.user.username

    def addKarma(self, num):
        self.karma += num
        self.save()

    def reduceKarma(self, num):
        if self.karma - num >= 0:
            self.karma -= num
        else:
            self.karma = 0
        self.save()
