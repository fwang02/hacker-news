from django.contrib import admin


from news.models import *

# Register your models here.
admin.site.register(Submission)
admin.site.register(Submission_URL)
admin.site.register(Submission_ASK)
admin.site.register(HiddenSubmission)
admin.site.register(Comment)
admin.site.register(UpvotedSubmission)
admin.site.register(UpvotedComment)

