from django.contrib import admin
from .models import Submission, Submission_URL, Submission_ASK, HiddenSubmission

from news.models import Submission

from news.models import Submission

# Register your models here.
admin.site.register(Submission)
admin.site.register(Submission_URL)
admin.site.register(Submission_ASK)
admin.site.register(HiddenSubmission)
