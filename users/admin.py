from django.contrib import admin
from users.models import *

# Register your models here.
admin.site.register(Favorite_submission)
admin.site.register(Favorite_comment)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'karma', 'about', 'banner', 'avatar']
    search_fields = ['user__username', 'karma']
    list_filter = ['karma']
    list_editable = ['karma']
    list_per_page = 10
    list_max_show_all = 100
    