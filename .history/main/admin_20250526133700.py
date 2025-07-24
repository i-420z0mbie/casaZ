from django.contrib import admin
from . import models
from django.urls import path
from django.template.response import TemplateResponse
from django.utils import timezone
from django.db.models import Count
from .models import Property, Inquiry, Message, SavedProperty

class ZombieAdminSite(admin.AdminSite):
    site_header = "z0mbie Admin"
    index_title = "Live Dashboard"
    site_title = "z0mbie ReState"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom + urls

    def dashboard_view(self, request):
        # Gather real-time stats
        now = timezone.now()
        total_properties = Property.objects.count()
        inquiries_today = Inquiry.objects.filter(created_at__date=now.date()).count()
        unread_messages = Message.objects.filter(read=False).count()
        favorites = SavedProperty.objects.aggregate(total=Count('id'))['total']

        # Prepare data for Chart.js (monthly inquiries example)
        monthly = (
            Inquiry.objects
            .filter(created_at__year=now.year)
            .annotate(month=Count('created_at__month'))
            .values_list('created_at__month', 'month')
        )
        # Build a simple mapping month → count
        inquiry_by_month = {m: c for m, c in monthly}

        context = dict(
            self.each_context(request),
            total_properties=total_properties,
            inquiries_today=inquiries_today,
            unread_messages=unread_messages,
            favorites=favorites,
            inquiry_by_month=inquiry_by_month,
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

# instantiate and register
admin_site = ZombieAdminSite(name='zombie_admin')

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