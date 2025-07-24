from django.urls import path, include
from .views import verify_subscription_payment, verify_listing_payment, PropertyViewSet, ProperyFeatureViewSet, PropertyImageViewSet, PropertyReviewViewset, RegionViewSet, SavedPropertyViewSet, CityViewSet, MessageViewSet, NotificationViewSet, SubscriptionPaymentViewSet,  UserSubscriptionViewSet, SubscriptionPlanViewSet, ListingPaymentViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('property_features', viewset=ProperyFeatureViewSet, basename='property_features')
router.register('properties', viewset=PropertyViewSet, basename='properties')
router.register('regions', viewset=RegionViewSet, basename='regions')
router.register('cities', viewset=CityViewSet, basename='cities')
router.register('messages', viewset=MessageViewSet, basename='messages')
router.register('notifications', viewset=NotificationViewSet, basename='notifications')
router.register('subscription-plans', viewset=SubscriptionPlanViewSet, basename='subscription_plan')
router.register('subscription-payments', viewset=SubscriptionPaymentViewSet, basename='subscriptions_payment')
router.register('user-subscriptions', viewset=UserSubscriptionViewSet, basename='user_subscriptions')
router.register('listing-payments', viewset=ListingPaymentViewSet, basename='listing-payments')

property_router = routers.NestedDefaultRouter(router, 'properties', lookup='property')
property_router.register('images', viewset=PropertyImageViewSet, basename='images')
property_router.register('reviews', viewset=PropertyReviewViewset, basename='reviews')
property_router.register('favorites', viewset=SavedPropertyViewSet, basename='favorites')


urlpatterns = [
    path('payments/verify-listing/', verify_listing_payment, name='verify-listing'),
    path('payments/verify-subscription/', verify_subscription_payment, name='verify-subscription'),
    path('', include(router.urls)),
    path('', include(property_router.urls)),
]

from django.urls import path, include
from .views import verify_subscription_payment, verify_listing_payment, PropertyViewSet, ProperyFeatureViewSet, PropertyImageViewSet, PropertyReviewViewset, RegionViewSet, SavedPropertyViewSet, CityViewSet, MessageViewSet, PushTokenViewSet, NotificationViewSet, SubscriptionPaymentViewSet,  UserSubscriptionViewSet, SubscriptionPlanViewSet, ListingPaymentViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('property_features', viewset=ProperyFeatureViewSet, basename='property_features')
router.register('properties', viewset=PropertyViewSet, basename='properties')
router.register('regions', viewset=RegionViewSet, basename='regions')
router.register('cities', viewset=CityViewSet, basename='cities')
router.register('messages', viewset=MessageViewSet, basename='messages')
router.register('notifications', viewset=NotificationViewSet, basename='notifications')
router.register('subscription-plans', viewset=SubscriptionPlanViewSet, basename='subscription_plan')
router.register('subscription-payments', viewset=SubscriptionPaymentViewSet, basename='subscriptions_payment')
router.register('user-subscriptions', viewset=UserSubscriptionViewSet, basename='user_subscriptions')
router.register('listing-payments', viewset=ListingPaymentViewSet, basename='listing-payments')
router.register('push-tokens', PushTokenViewSet, basename='push-token')

property_router = routers.NestedDefaultRouter(router, 'properties', lookup='property')
property_router.register('images', viewset=PropertyImageViewSet, basename='images')
property_router.register('reviews', viewset=PropertyReviewViewset, basename='reviews')
property_router.register('favorites', viewset=SavedPropertyViewSet, basename='favorites')


urlpatterns = [
    path('payments/verify-listing/', verify_listing_payment, name='verify-listing'),
    path('payments/verify-subscription/', verify_subscription_payment, name='verify-subscription'),
    path('', include(router.urls)),
    path('', include(property_router.urls)),
]

