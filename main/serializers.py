from rest_framework import serializers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from . import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PropertyFeature
        fields = ['id', 'name']
        read_only_fields = ['id']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PropertyImage
        fields = ['id', 'property', 'images', 'created_at']
        read_only_fields = ['id', 'property', 'created_at']

    def create(self, validated_data):
        property_id = self.context.get('property_id')

        if not property_id:
            raise serializers.ValidationError({'detail': 'Missing property_id in context.'})

        return models.PropertyImage.objects.create(property_id=property_id, **validated_data)


class PropertyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PropertyReview
        fields = ['id', 'author', 'property', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'author', 'property', 'created_at']

    
    def create(self, validated_data):
        property_id = self.context['property_id']

        return models.PropertyReview.objects.create(property_id=property_id, **validated_data)

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = models.City
        fields = ['id', 'region', 'city']

class PropertySerializer(serializers.ModelSerializer):
    
    reviews = PropertyReviewSerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, source='properties', read_only=True)
    features = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.PropertyFeature.objects.all()
    )



    class Meta:
        model = models.Property

        fields = ['id', 'creator', 'title', 
                  'description', 'type', 
                  'price', 'number_of_bedrooms', 
                  'number_of_bathrooms', 'property_type',
                  'features', 'images', 'city', 'detailed_address',
                  'status', 'is_verified', 'is_featured', 'slug', 'date_posted', 'reviews']
        
        read_only_fields = ['id', 'creator', 'is_verified', 'is_featured', 'date_posted']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['features'] = list(instance.features.all().values('id', 'name'))
        rep['city'] = CitySerializer(instance.city).data if instance.city else None
        return rep

    

class SavedPreopertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SavedProperty
        fields = ['id', 'creator', 'property', 'created_at']
        read_only_fields = ['id', 'creator', 'property', 'created_at']

    def create(self, validated_data):
        property_id = self.context['property_id']

        return models.SavedProperty.objects.create(property_id=property_id, **validated_data)







class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Inquiry
        fields = ['id', 'name', 'email', 'phone', 'message', 'property', 'created_at']
        read_only_fields = ['id', 'property', 'created_at']

    
    def create(self, validated_data):
        property_id = self.context['property_id']

        return models.Inquiry.objects.create(property=property_id, **validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)


    class Meta:
        model = models.Message
        fields = [
            'id', 
            'sender',          # numeric ID, read-only since you set sender in perform_create
            'recipient',       # numeric ID
            'content',
            'sender_username', 
            'recipient_username', 
            'timestamp', 
            'is_read', 'avatar_url',
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'sender_username', 'recipient_username']




class NotificationSerializer(serializers.ModelSerializer):
    object_data = serializers.SerializerMethodField()

    class Meta:
        model = models.Notification
        fields = [
            'id', 'user', 'notif_type', 'object_id', 'object_data',
            'timestamp', 'is_read'
        ]
        read_only_fields = ['id', 'user', 'timestamp', 'object_data']

    def get_object_data(self, obj):

        if obj.notif_type == models.Notification.NOTIF_VERIFIED:
            return {
                'title': obj.content_object.title,
                'slug': obj.content_object.slug,
            }
        elif obj.notif_type == models.Notification.NOTIF_FAVORITE:
            return {
                'title': obj.content_object.property.title,
                'slug': obj.content_object.property.slug,
            }
        return {}

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)







