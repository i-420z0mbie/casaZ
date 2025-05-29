from django.db import models
from django.utils.text import slugify
import uuid
from .storages import MediaStorage
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
        (TYPE_COMMERCIAL, 'commercial')
    ]

    STATUS_AVAILABLE = 'available'
    STATUS_NOT_AVAILABLE = 'not available'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'available'),
        (STATUS_NOT_AVAILABLE, 'not availble'),

    ]

    creator = models.ForeignKey(CompleteUser, on_delete=models.CASCADE, related_name='creators')
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TYPE_RENTAL)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_bedrooms = models.PositiveIntegerField(default=1)
    number_of_bathrooms = models.PositiveIntegerField(default=1)
    property_type = models.CharField(max_length=100, choices=PROPERTY_TYPE_CHOICES, default=TYPE_APARTMENT)
    features = models.ManyToManyField(PropertyFeature, related_name='property_features', blank=True)
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='cities')
    detailed_address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
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
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='properties')
    images     = models.ImageField(
                    upload_to='restate_ads/',
                    storage=MediaStorage(),
                )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.property}-{self.images}'
    

    
    objects = models.Manager()


class PropertyReview(models.Model):
    author = models.ForeignKey(CompleteUser, on_delete=models.CASCADE, related_name='authors')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')   
    rating = models.PositiveSmallIntegerField(default=1)
    review = models.TextField(blank=True, null=True) 
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if self.rating > 5:
            raise ValidationError("Ratings must not exceed 5")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.author}-{self.rating}'

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


    


class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'From {self.sender} to {self.recipient} at {self.timestamp}'
    

    objects = models.Manager()


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.UUIDField(null=True)  # ✅ This was PositiveIntegerField
    content_object = GenericForeignKey('content_type', 'object_id')

    NOTIF_VERIFIED = 'verified'
    NOTIF_FAVORITE = 'favorite'
    TYPE_CHOICES = [
        (NOTIF_VERIFIED, 'Property Verified'),
        (NOTIF_FAVORITE, 'Added to Favorites'),
    ]
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification {self.notif_type} to {self.user} on {self.timestamp}"
