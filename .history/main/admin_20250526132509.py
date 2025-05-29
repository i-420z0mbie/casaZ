from django.contrib import admin
from . import models
from django.urls import reverse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Property, CompleteUser, Inquiry, Message

@admin.site.admin_view
def custom_admin_dashboard(request):
    # Get statistics data
    context = {
        'total_properties': Property.objects.count(),
        'active_users': CompleteUser.objects.filter(is_active=True).count(),
        'new_inquiries': Inquiry.objects.filter(status='new').count(),
        'total_messages': Message.objects.count(),
        
        # Dummy data for example - replace with real queries
        'recent_activities': [
            {'icon': 'user-plus', 'text': 'New user registered', 'time': '2h ago'},
            {'icon': 'home', 'text': 'Property #123 added', 'time': '4h ago'},
            {'icon': 'comment', 'text': 'New inquiry received', 'time': '1d ago'},
        ],
        # 'property_types': {
        #     'residential': 45,
        #     'commercial': 25,
        #     'vacation': 15,
        #     'luxury': 15
        # }
    }
    return render(request, 'admin/dashboard.html', context)

# Replace default admin index
admin.site.index = custom_admin_dashboard

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