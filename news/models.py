from django.db import models

# Create your models here.
class Submission(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    text = models.TextField()  # Ensure this field is defined
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/news/{self.id}"