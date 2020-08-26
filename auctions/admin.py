from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email", "is_superuser", "is_staff", "is_active")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "bid_amount", "timestamp")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "comment", "timestamp")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "title", "starting_bid", "category", "timestamp", "active")

# Register your models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Bid, BidAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Listing, ListingAdmin)