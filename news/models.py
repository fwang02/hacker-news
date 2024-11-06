from django.db import models
from django.contrib.auth.models import User

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission_URL(Submission):
    pass

class Submission_ASK(Submission):
    pass