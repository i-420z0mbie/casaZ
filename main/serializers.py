from rest_framework import serializers
import uuid
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from . import models
from datetime import timedelta
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
        fields = ['id', 'author', 'property', 'review', 'created_at', ]
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
    expiry_date = serializers.DateTimeField(read_only=True)
    images = PropertyImageSerializer(many=True,  read_only=True)
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
                  'status', 'is_verified', 'is_featured', 'visit_count', 'condition',
                    'is_promoted', 'is_recommended', 'expiry_date', 
                    'slug', 'date_posted', 'reviews',
                    'square_meters', 'parking_spaces', 'has_garage', 'wheelchair_access',
                    'elevator', 'secure_parking', 'floor_number', 'year_built']
        
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

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     validated_data['user'] = user
    #     return super().create(validated_data)


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PushToken
        fields = ['id', 'token']



class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Perk
        fields = ['id', 'code', 'label', 'has_badge', 'has_double_badge']



class SubscriptionPlanSerializer(serializers.ModelSerializer):

    perks = PerkSerializer(many=True, read_only=True)


    class Meta:
        model = models.SubscriptionPlan
        fields = ['id', 'slug', 'display_name', 'description', 'price', 'duration_days', 'number_of_free_listings',
                  'unlimited_listings', 'is_active', 'perks', 'created_at', 'updated_at']



class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=models.SubscriptionPlan.objects.filter(is_active=True),
        source='plan',
        write_only=True
    )

    class Meta:
        model = models.UserSubscription
        fields = [
            'id', 'plan', 'plan_id', 'user',
            'start_date', 'end_date', 'is_active'
        ]
        read_only_fields = ['start_date', 'end_date', 'is_active']


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=models.SubscriptionPlan.objects.filter(is_active=True),
        write_only=True
    )
    subscription = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    promo_code = serializers.CharField(
        write_only=True, required=False
    )
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        read_only=True
    )

    class Meta:
        model = models.SubscriptionPayment
        fields = [
            'id', 'user', 'plan', 'subscription', 'amount',
            'promo_code', 'payment_ref', 'status', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'amount', 'payment_ref',
            'status', 'created_at', 'subscription'
        ]

    def validate_promo_code(self, code):
        try:
            return models.PromoCode.objects.get(code__iexact=code, is_active=True)
        except models.PromoCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired promo code")


class ListingPaymentSerializer(serializers.ModelSerializer):
    promo_code = serializers.CharField(
        write_only=True, required=False,
        help_text="Enter a marketer code for discount"
    )

    property_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Property.objects.all(),
        source='property', write_only=True
    )

    class Meta:
        model = models.ListingPayment
        fields = [
            'id', 'user', 'property', 'property_id',
            'promo_code', 'amount', 'payment_ref',
            'status', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'property', 'payment_ref',
            'status', 'created_at',
        ]

    def validate_promo_code(self, code):
        try:
            return models.PromoCode.objects.get(code__iexact=code, is_active=True)
        except models.PromoCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired promo code")

    def create(self, validated_data):
        """
        1) Determine base amount from the Property
        2) In a transaction, lock the promo row and check one‐time use
        3) Create the ListingPayment with base amount and a generated ref
        4) Apply promo.apply(...) to update amount & promo_code
        """
        promo = validated_data.pop('promo_code', None)
        prop = validated_data['property']
        user = validated_data['user']

        # 1) Base amount determined by the property’s fee/price
        #    (assuming `Property` has a `price` field)
        base_amount = prop.price

        with transaction.atomic():
            if promo:
                # 2a) Lock promo row
                promo = models.PromoCode.objects.select_for_update().get(pk=promo.pk)

                # 2b) Enforce one‐time‐use per user on listings
                if models.ListingPayment.objects.filter(user=user, promo_code=promo).exists():
                    raise ValidationError("You have already used this promo code.")

            # 3) Create payment record
            payment = models.ListingPayment.objects.create(
                user=user,
                property=prop,
                amount=base_amount,
                payment_ref=uuid.uuid4().hex,
                status='pending'
            )

            # 4) Apply promo discount if present
            if promo:
                payment.amount = promo.apply(payment.amount)
                payment.promo_code = promo
                payment.save(update_fields=['amount', 'promo_code'])

        return payment