from django.contrib import admin
from . import models
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count

class CustomAdminSite(admin.AdminSite):
    site_header = "z0mbie Admin"
    site_title = "ReState Admin"
    index_title = "Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Live statistics
        from main.models import Property, Inquiry, Message
        stats = {
            'properties': Property.objects.count(),
            'inquiries':  Inquiry.objects.count(),
            'messages':   Message.objects.count(),
        }
        # For chart: count per city
        city_data = Property.objects.values('city__name').annotate(total=Count('id'))
        return TemplateResponse(request, 'admin/dashboard.html', {
            'stats': stats,
            'city_data': list(city_data),
        })

# Instantiate and register
custom_admin_site = CustomAdminSite(name='custom_admin')

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
class PropertyFeature(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(models.PropertyImage)
class PropertyImage(admin.ModelAdmin):
    list_display = ['property', 'images']
    search_fields = ['property']


@admin.register(models.Region)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']

@admin.register(models.SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ['creator', 'property']


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type']