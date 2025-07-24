from django.db import models
from django.utils.text import slugify
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


class CompleteUser(AbstractUser):

    ACCOUNT_REGULAR = 'regular'
    ACCOUNT_AGENT = 'agent'
    ACCOUNT_LANDLORD = 'landlord'

    ACCOUNT_CHOICES = [
        (ACCOUNT_REGULAR, 'regular'),
        (ACCOUNT_AGENT, 'agent'),
        (ACCOUNT_LANDLORD, 'landlord')
    ]

    account_type = models.CharField(max_length=50, choices=ACCOUNT_CHOICES, default=ACCOUNT_REGULAR)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    

    


class PropertyFeature(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'
    
    objects = models.Manager()



class Property(models.Model):

    def default_expiry():
        return timezone.now() + timedelta(days=14)

    TYPE_RENTAL = 'rental'
    TYPE_SHORT_RENTAL = 'short rental'
    TYPE_SALE = 'sale'

    TYPE_CHOICES = [
        (TYPE_RENTAL, 'rental'),
        (TYPE_SHORT_RENTAL, 'short rental'),
        (TYPE_SALE, 'sale')
    ]

    TYPE_SINGLE_ROOM = 'single room'
    TYPE_SELF_CONTAINED = 'self contained'
    TYPE_CHAMBER_AND_HALL = 'chamber & hall'
    TYPE_APARTMENT = 'apartment'
    TYPE_SERVICED_APARTMENT = 'serviced apartment'
    TYPE_DUPLEX = 'duplex'
    TYPE_HOSTEL = 'hostel'
    TYPE_GUEST_HOUSE = 'guest house'
    TYPE_AIRBNB = 'air-bnb'
    TYPE_COMMERCIAL = 'commercial'

    PROPERTY_TYPE_CHOICES = [
        (TYPE_SINGLE_ROOM, 'single room'),
        (TYPE_SELF_CONTAINED, 'self contained'),
        (TYPE_CHAMBER_AND_HALL, 'chamber & hall'),
        (TYPE_APARTMENT, 'apartment'),
        (TYPE_SERVICED_APARTMENT, 'serviced apartment'),
        (TYPE_DUPLEX, 'duplex'),
        (TYPE_HOSTEL, 'hostel'),
        (TYPE_GUEST_HOUSE, 'guest house'),
        (TYPE_COMMERCIAL, 'commercial'),
        (TYPE_AIRBNB, 'air-bnb')
    ]

    STATUS_AVAILABLE = 'available'
    STATUS_NOT_AVAILABLE = 'not available'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'available'),
        (STATUS_NOT_AVAILABLE, 'not availble'),

    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('needs_renovation', 'Needs Renovation'),
    ]

    creator = models.ForeignKey(CompleteUser, on_delete=models.CASCADE, related_name='properties')
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TYPE_RENTAL)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_bedrooms = models.PositiveIntegerField(default=1)
    number_of_bathrooms = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    property_type = models.CharField(max_length=100, choices=PROPERTY_TYPE_CHOICES, default=TYPE_APARTMENT)
    features = models.ManyToManyField(PropertyFeature, related_name='property_features', blank=True)
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='cities')
    visit_count = models.PositiveIntegerField(default=0, help_text="Total number of times this property has been viewed")
    detailed_address = models.TextField(blank=True, null=True)
    square_meters = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    parking_spaces = models.PositiveIntegerField(default=0)
    has_garage = models.BooleanField(default=False)
    wheelchair_access = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    secure_parking = models.BooleanField(default=False, help_text="Gated or guarded parking")
    floor_number = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
    year_built = models.PositiveIntegerField(null=True, blank=True)
    is_recommended = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(default=default_expiry)
    slug = models.SlugField(unique=True, blank=True)
    date_posted = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'properties'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}-{self.type}-{self.property_type}'

    objects = models.Manager()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    images     = models.ImageField(
                    upload_to='restate_ads/',
                    # storage=MediaStorage(),
                )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.property}-{self.images}'
    

    
    objects = models.Manager()


class PropertyReview(models.Model):
    author = models.ForeignKey(CompleteUser, on_delete=models.CASCADE, related_name='authors')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')   
    review = models.TextField(blank=True, null=True) 
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}-{self.review}'

    objects = models.Manager()


class SavedProperty(models.Model):
    creator = models.ForeignKey(CompleteUser, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorite_properties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.creator}-{self.property}'
    
    class Meta:
        verbose_name_plural = 'saved properties'

        unique_together = ('creator', 'property')
    
    objects = models.Manager()


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'
    
    objects = models.Manager()


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='regions')
    city = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.region}-{self.city}'
    

    class Meta:
        verbose_name_plural = 'cities'
    
    objects = models.Manager()


class Inquiry(models.Model):
    name = models.CharField(max_length=255)
    Email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=13)
    message = models.TextField()
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_inquiries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}-{self.message}'
    
    class Meta:
        verbose_name_plural = 'inquiries'
    
    objects = models.Manager()


    


class PushToken(models.Model):
    """
    Stores an Expo push token for each user/device.
    """
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='push_tokens', on_delete=models.CASCADE)
    token     = models.CharField(max_length=255, unique=True)
    created   = models.DateTimeField(auto_now_add=True)
    updated   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} → {self.token}'


class Message(models.Model):
    id          = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    sender      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)
    avatar_url  = models.URLField(blank=True, null=True)
    is_read     = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'From {self.sender} to {self.recipient} at {self.timestamp}'


class Notification(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    content_type  = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id     = models.UUIDField(null=True)
    content_object= GenericForeignKey('content_type', 'object_id')

    NOTIF_VERIFIED = 'verified'
    NOTIF_FAVORITE = 'favorite'
    TYPE_CHOICES   = [
        (NOTIF_VERIFIED, 'Property Verified'),
        (NOTIF_FAVORITE, 'Added to Favorites'),
    ]
    notif_type    = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    timestamp     = models.DateTimeField(auto_now_add=True)
    is_read       = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification {self.notif_type} to {self.user} on {self.timestamp}"



class PromoCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    discount_percent = models.PositiveSmallIntegerField(help_text="0–100")
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1, help_text="How many times it can be used")
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)

    def apply(self, amount):
        if not self.is_active:
            raise ValueError("Promo code is inactive.")
        if self.expires_at and timezone.now() > self.expires_at:
            raise ValueError("Promo code has expired.")
        if self.used_count >= self.usage_limit:
            raise ValueError("Promo code usage limit reached.")

        discounted = amount * (100 - self.discount_percent) / 100
        self.used_count += 1
        if self.used_count >= self.usage_limit:
            self.is_active = False
        self.save(update_fields=['used_count', 'is_active'])
        return round(discounted, 2)

    def __str__(self):
        return f'{self.code}'



class Perk(models.Model):
    code = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    has_badge = models.BooleanField(default=False)
    has_double_badge = models.BooleanField(default=False)
    description = models.TextField()


    objects = models.Manager()

    def __str__(self):
        return f'{self.code}-{self.label}'



class SubscriptionPlan(models.Model):
    slug = models.SlugField(max_length=30, unique=True)
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30, help_text='How many days the plan lasts per purchase')
    number_of_free_listings = models.PositiveIntegerField(default=1, help_text='0 means unlimited listings')
    unlimited_listings = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    perks = models.ManyToManyField(Perk, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['price']

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.display_name)

        super().save(*args, **kwargs)

    
    def __str__(self):
        return f'{self.display_name}-{self.price}'
    

    objects = models.Manager()



class UserSubscription(models.Model):
    user = models.ForeignKey(
        CompleteUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT
    )
    start_date = models.DateTimeField(
        default=timezone.now
    )
    end_date = models.DateTimeField()
    is_active = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        # First creation: set end_date based on plan duration
        if not self.pk:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def has_free_quota(self):
        # Unlimited plans always allow
        if self.plan.unlimited_listings:
            return True

        # Sum allowances across all active subscriptions
        active = self.user.subscriptions.filter(is_active=True)
        total_allowed = sum(
            s.plan.number_of_free_listings for s in active
        )

        # Find earliest start_date among active subs
        earliest = active.order_by('start_date').first()
        if earliest:
            used = self.user.properties.filter(
                date_posted__gte=earliest.start_date.date()
            ).count()
        else:
            used = 0

        return used < total_allowed




class SubscriptionPayment(models.Model):
    user = models.ForeignKey(CompleteUser, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    payment_ref = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('succes', 'Success'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}-{self.subscription}-{self.amount}'
    
    objects = models.Manager()





class ListingPayment(models.Model):
    user = models.ForeignKey(CompleteUser, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    amount       = models.DecimalField(max_digits=12, decimal_places=2)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    payment_ref  = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status       = models.CharField(max_length=20, choices=[
                        ('pending','Pending'),
                        ('success','Success'),
                        ('failed','Failed'),
                    ], default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → listing {self.property.id} ({self.status})"
    

    objects = models.Manager()
