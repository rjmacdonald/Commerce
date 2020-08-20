from django.contrib import admin
from . import models

class UserAdmin (admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email", "is_superuser", "is_staff", "is_active")

# Register your models here.
admin.site.register(models.User, UserAdmin)