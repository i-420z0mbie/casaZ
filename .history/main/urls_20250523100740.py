from django.urls import path, include
from .views import PropertyViewSet, ProperyFeatureViewSet, PropertyImageViewSet, PropertyReviewViewset, RegionViewSet, SavedPropertyViewSet, CityViewSet, InquiryViewSet, MessageViewSet, NotificationViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('property_features', viewset=ProperyFeatureViewSet, basename='property_features')
router.register('properties', viewset=PropertyViewSet, basename='properties')
router.register('regions', viewset=RegionViewSet, basename='regions')
router.register('cities', viewset=CityViewSet, basename='cities')
# router.register('inquiries', viewset=InquiryViewSet, basename='inquiries')
router.register('messages', viewset=MessageViewSet, basename='messages')
router.register('notifications', viewset=NotificationViewSet, basename='notifications')

property_router = routers.NestedDefaultRouter(router, 'properties', lookup='property')
property_router.register('images', viewset=PropertyImageViewSet, basename='images')
property_router.register('reviews', viewset=PropertyReviewViewset, basename='reviews')
property_router.register('favorites', viewset=SavedPropertyViewSet, basename='favorites')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(property_router.urls)),
]