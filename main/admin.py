from django.contrib import admin
from . import models


@admin.register(models.CompleteUser)
class CompleteUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'account_type']
    search_fields = ['username']
    list_filter = ['account_type']


@admin.register(models.Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['creator', 'title', 'is_verified', 'is_promoted', 'is_featured', 'is_recommended', 'property_type', 'date_posted']
    list_editable = ['is_verified', 'is_featured', 'is_recommended', 'is_promoted',]
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


admin.site.register(models.PushToken)


@admin.register(models.PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['review']


@admin.register(models.ListingPayment)
class ListingPaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'amount', 'status']


@admin.register(models.Perk)
class PerkAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'has_badge', 'has_double_badge']



@admin.register(models.SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['slug', 'display_name', 'price', 'is_active', 'duration_days']


@admin.register(models.UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'has_free_quota']
    list_editable = ['is_active']


@admin.register(models.SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'amount', 'status']


@admin.register(models.PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'usage_limit', 'used_count', 'is_active']
    list_editable = ['is_active']