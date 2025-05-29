from django.contrib import admin
from . import models

@admin.register(models.CompleteUser)
class CompleteUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'account_type']
    search_fields = ['username']
    list_filter = ['account_type']


@admin.register(models.Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['creator', 'title', 'type', 'is_verified', 'is_featured', 'property_type', 'date_posted']
    list_editable = ['is_verified', 'is_featured']
    search_fields = ['creator', 'type', 'property_type']
    list_filter = ['date_posted', 'is_featured', 'price']

@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['region', 'city']
    list_filter = ['region', 'city']

admin.site.register(models.Inquiry)

@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'timestamp', 'is_read']
    list_filter = ['timestamp']

@admin.register(models.PropertyFeature)

# admin.site.register(models.PropertyImage)

# admin.site.register(models.Region)

# admin.site.register(models.SavedProperty)

# admin.site.register(models.Notification)
