import requests
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, parsers
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Max
from . filters import PropertyFilter
from django.db import transaction
from datetime import timedelta
import uuid
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import requests, logging
from django.conf import settings

logger = logging.getLogger(__name__) 
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta
from . import models
from . import serializers
import logging

logger = logging.getLogger(__name__)


User = get_user_model()


class ProperyFeatureViewSet(ModelViewSet):
    queryset = models.PropertyFeature.objects.all()
    serializer_class = serializers.PropertyFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    


MAX_IMAGES_PER_PROPERTY = 4

class PropertyViewSet(ModelViewSet):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'type', 'property_type']
    ordering_fields = ['price', 'date_posted', 'type', 'property_type']

    def get_queryset(self):
        qs = super().get_queryset()
        now = timezone.now()

        if self.request.user.is_staff:
            return qs
        if self.action == 'my_properties':
            return qs.filter(creator=self.request.user)
        return qs.filter(is_verified=True, expiry_date__gt=now)

    def perform_create(self, serializer):
        user = self.request.user
        prop = serializer.save(creator=user)
        sub = models.UserSubscription.objects.filter(user=user, is_active=True).first()
        if sub and sub.has_free_quota():
            codes = sub.plan.perks.values_list('code', flat=True)
            prop.is_featured = 'featured' in codes
            prop.is_recommended = 'recommended' in codes
            prop.is_promoted = 'promoted' in codes
            prop.save(update_fields=['is_featured', 'is_recommended', 'is_promoted'])

    def perform_update(self, serializer):
        if serializer.instance.creator != self.request.user:
            raise PermissionDenied('You do not have permission to edit this property.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            raise PermissionDenied('You do not have permission to delete this property.')
        instance.delete()

    @action(detail=True, methods=['post'])
    def visit(self, request, pk=None):
        """Increment and return the new visit count."""
        prop = self.get_object()
        # Optionally: throttle by IP / user to avoid bots
        prop.visit_count = F('visit_count') + 1
        prop.save(update_fields=['visit_count'])
        prop.refresh_from_db()  # get the actual integer value
        return Response({'visit_count': prop.visit_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-properties')
    def my_properties(self, request):
        queryset = self.get_queryset().filter(creator=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        url_path='add_images',
        parser_classes=[parsers.MultiPartParser, parsers.FormParser]
    )
    def add_images(self, request, pk=None):
        prop = get_object_or_404(models.Property, pk=pk)
        if prop.creator != request.user:
            raise PermissionDenied("You do not have permission to add images to this property.")

        existing_count = prop.images.count()
        files = request.FILES.getlist('images')
        total_after = existing_count + len(files)
        if total_after > MAX_IMAGES_PER_PROPERTY:
            return Response(
                {"detail": f"Maximum of {MAX_IMAGES_PER_PROPERTY} images allowed. You have {existing_count} already."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        for img in files:
            ser = serializers.PropertyImageSerializer(data={'images': img}, context={'property_id': prop.pk, 'request': request})
            ser.is_valid(raise_exception=True)
            ser.save()
            created.append(ser.data)

        return Response(created, status=status.HTTP_201_CREATED)
    
   



class PropertyImageViewSet(ModelViewSet):
    serializer_class = serializers.PropertyImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        property_pk = self.kwargs.get('property_pk')
        return models.PropertyImage.objects.filter(property_id=property_pk) if property_pk else models.PropertyImage.objects.none()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        if self.kwargs.get('property_pk'):
            ctx['property_id'] = self.kwargs['property_pk']
        return ctx

    def perform_create(self, serializer):
        prop = get_object_or_404(models.Property, pk=self.kwargs['property_pk'])
        if prop.creator != self.request.user:
            raise PermissionDenied("You do not have permission to add images to this property.")
        serializer.save(property=prop)

    def perform_destroy(self, instance):
        if instance.property.creator != self.request.user:
            raise PermissionDenied("You do not have permission to delete images from this property.")
        instance.delete()


class PropertyReviewViewset(ModelViewSet):
    queryset = models.PropertyReview.objects.all()
    serializer_class = serializers.PropertyReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return models.PropertyReview.objects.filter(property_id=self.kwargs['property_pk'])
    
    def get_serializer_context(self):
        return {'property_id': self.kwargs['property_pk']}


    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(author=user)

    def perform_update(self, serializer):
        user = self.request.user

        if serializer.instance.author != user:
            raise PermissionDenied({'Denied': 'You do not have the permission to edit this post'})
        
        serializer.save()

    
    def perform_destroy(self, instance):
        user = self.request.user

        if instance.author != user:
            raise PermissionDenied({"Denied": "You do not have the permission to delete this post!"})
        
        instance.delete()
    


class SavedPropertyViewSet(ModelViewSet):
    queryset = models.SavedProperty.objects.all()
    serializer_class = serializers.SavedPreopertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.SavedProperty.objects.filter(
            property_id=self.kwargs['property_pk'],
            creator=self.request.user
    )
    
    def get_serializer_context(self):
        return {'property_id': self.kwargs['property_pk']}
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            raise PermissionDenied("You do not have permission to unsave this.")
        instance.delete()

    @action(detail=False, methods=['post'], url_path='favorite')
    def favorite_property(self, request, property_pk=None):
        user = request.user

        prop = models.Property.objects.get(pk=property_pk)
        saved_obj, created = models.SavedProperty.objects.get_or_create(
            creator=user,
            property=prop
        )
        if not created:
            return Response({"detail": "Already favorited"}, status=200)

        # *** use the same "notif_user_{id}" naming that your consumer expects ***
        channel_layer = get_channel_layer()
        owner_id = prop.creator.id
        async_to_sync(channel_layer.group_send)(
            f"notif_user_{owner_id}",    # ← changed here
            {
                "type": "favorite.notify",        
                "notification": {
                  "propertyId": str(prop.pk),
                  "title": f"{user.username} favorited your property!",
                  "timestamp": timezone.now().isoformat(),
                }
            }
        )

        return Response(
          {"detail": "Property favorited and notification sent"},
          status=201
        )
    

class RegionViewSet(ReadOnlyModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    

class CityViewSet(ReadOnlyModelViewSet):
    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer


class InquiryViewSet(ModelViewSet):
    queryset = models.Inquiry.objects.all()
    serializer_class = serializers.InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Inquiry.objects.filter(property_id=self.kwargs['property_pk'])
    
    def get_serializer_context(self):
        return {'property_id': self.kwargs['self.property_pk']}
    

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(user)



class MessageViewSet(ModelViewSet):
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Start with all messages where you're either sender or recipient
        qs = models.Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )
        # Optional: if they *do* pass ?user_id=XYZ, further narrow to that 1-1 thread
        other_id = self.request.query_params.get('user_id')
        if other_id:
            qs = qs.filter(
                (Q(sender=user,    recipient_id=other_id) |
                 Q(sender_id=other_id, recipient=user))
            )
        return qs.order_by('timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # if this is a 1-1 fetch, mark unseen messages as read:
        other_id = request.query_params.get('user_id')
        if other_id:
            queryset.filter(
                recipient=request.user, is_read=False
            ).update(is_read=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'current_user': request.user.id,
            'messages': serializer.data
    })

    def create(self, request, *args, **kwargs):
        recipient_id = (
            request.data.get('recipient') or
            request.query_params.get('user_id')
        )
        if not recipient_id:
            raise ValidationError({"recipient": "This field is required."})

        recipient = get_object_or_404(User, pk=recipient_id)
        mutable = request.data.copy()
        mutable['recipient'] = recipient_id
        request._full_data = mutable  # DRF uses _full_data internally

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        if instance.sender != user and instance.recipient != user:
            raise PermissionDenied("You cannot update this message.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.sender != user:
            raise PermissionDenied("You cannot delete this message.")
        instance.delete()






class NotificationViewSet(ModelViewSet):
    # class‑level “good” notifications
    queryset = models.Notification.objects.filter(
        content_type__isnull=False,
        object_id__isnull=False,
    )
    serializer_class   = serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # super().get_queryset() applies that class‑level filter first
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def mark_read(self, request):
        ids = request.data.get('ids', [])
        models.Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
        return Response({'status': 'marked read'})



class SubscriptionPlanViewSet(ReadOnlyModelViewSet):
    queryset = models.SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = serializers.SubscriptionPlanSerializer



class UserSubscriptionViewSet(ModelViewSet):
    queryset = models.UserSubscription.objects.all()
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        now = timezone.now()
        subs = models.UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=now
        )

        if not subs.exists():
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        # aggregate across all active subs
        max_end = max(s.end_date for s in subs)
        total_allowed = sum(
            s.plan.number_of_free_listings for s in subs if not s.plan.unlimited_listings
        )
        unlimited = any(s.plan.unlimited_listings for s in subs)
        earliest_start = min(s.start_date for s in subs)
        used = request.user.properties.filter(
            date_posted__gte=earliest_start.date()
        ).count()

        remaining = None if unlimited else max(total_allowed - used, 0)

        data = {
            'id': subs[0].id,
            'plan': subs[0].plan.slug,
            'start_date': min(s.start_date for s in subs),
            'end_date': max_end,
            'is_active': True,
            'unlimited_listings': unlimited,
            'has_free_quota': unlimited or remaining > 0,
            'free_listings_remaining': remaining
        }
        return Response(data, status=status.HTTP_200_OK)
    



class SubscriptionPaymentViewSet(ModelViewSet):
    queryset = models.SubscriptionPayment.objects.all()
    serializer_class = serializers.SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Validate payload
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data.pop('plan')
        promo_code = serializer.validated_data.pop('promo_code', None)  # This is the PromoCode instance
        promo_obj = promo_code  # Use the instance directly instead of re-querying

        # Validate and apply promo
        amount = plan.price
        if promo_obj:
            try:
                with transaction.atomic():
                    # Lock the promo row for update
                    promo_obj = models.PromoCode.objects.select_for_update().get(pk=promo_obj.pk)
                    
                    # Check if user has already used this promo
                    if models.SubscriptionPayment.objects.filter(
                        user=request.user, promo_code=promo_obj
                    ).exists():
                        return Response(
                            {"detail": "Promo already used by you."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Check expiry
                    if promo_obj.expires_at and timezone.now() > promo_obj.expires_at:
                        return Response(
                            {"detail": "Promo expired."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Check usage limit
                    if promo_obj.used_count >= promo_obj.usage_limit:
                        return Response(
                            {"detail": "Promo usage limit reached."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Apply discount
                    amount = round(
                        plan.price * (100 - promo_obj.discount_percent) / 100,
                        2
                    )
                    
                    # Reserve promo usage
                    promo_obj.used_count += 1
                    promo_obj.save(update_fields=['used_count'])
            except models.PromoCode.DoesNotExist:
                return Response(
                    {"detail": "Promo code no longer available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create UserSubscription (inactive until payment completes)
        sub = models.UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            is_active=False
        )

        # Create SubscriptionPayment record
        payment = models.SubscriptionPayment.objects.create(
            user=request.user,
            subscription=sub,
            amount=amount,
            promo_code=promo_obj,  # Save promo object
            payment_ref=uuid.uuid4().hex,
            status='pending'
        )

        # Initialize Paystack transaction
        init_url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        init_payload = {
            "email": request.user.email,
            "amount": int(amount * 100),  # kobo
            "reference": payment.payment_ref,
        }
        if promo_obj:
            init_payload["metadata"] = {"promo_code": promo_obj.code}

        try:
            init_resp = requests.post(
                init_url, json=init_payload, headers=headers, timeout=10
            )
            init_json = init_resp.json()
            data = init_json.get("data", {})

            if init_resp.status_code != 200 or not data.get("access_code"):
                # Cleanup on failure
                payment.delete()
                sub.delete()
                if promo_obj:
                    # Rollback promo usage
                    promo_obj.used_count -= 1
                    promo_obj.save()
                return Response(
                    {
                        "error": "Could not initialize Paystack transaction",
                        "details": init_json,
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )
        except requests.exceptions.RequestException as e:
            payment.delete()
            sub.delete()
            if promo_obj:
                promo_obj.used_count -= 1
                promo_obj.save()
            return Response(
                {"error": "Payment gateway connection failed"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Return the access_code & reference for the frontend
        return Response(
            {
                "payment_ref": payment.payment_ref,
                "access_code": data["access_code"],
                "amount": amount,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def preview(self, request):
        """
        POST /subscription-payments/preview/
        Body: { "plan": <plan_id>, "promo_code": "<CODE>" }
        Returns: { "amount": discounted_amount }
        """
        plan_id = request.data.get('plan')
        code = request.data.get('promo_code', '').strip()

        # Validate plan
        try:
            plan = models.SubscriptionPlan.objects.get(
                pk=plan_id, is_active=True
            )
        except models.SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Plan not found or inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        base_amount = plan.price

        # No code → return base price
        if not code:
            return Response({"amount": base_amount}, status=status.HTTP_200_OK)

        # Validate promo code
        try:
            promo = models.PromoCode.objects.get(
                code__iexact=code, is_active=True
            )
            
            # One-time-per-user check
            if models.SubscriptionPayment.objects.filter(
                user=request.user, promo_code=promo
            ).exists():
                return Response(
                    {"detail": "Promo already used by you."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Expiry & usage-limit checks
            if promo.expires_at and timezone.now() > promo.expires_at:
                return Response(
                    {"detail": "Promo expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if promo.used_count >= promo.usage_limit:
                return Response(
                    {"detail": "Promo usage limit reached."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Compute discounted amount
            discounted = round(
                base_amount * (100 - promo.discount_percent) / 100,
                2
            )
            return Response({"amount": discounted}, status=status.HTTP_200_OK)
            
        except models.PromoCode.DoesNotExist:
            return Response(
                {"detail": "Invalid promo code."},
                status=status.HTTP_400_BAD_REQUEST
            )




class ListingPaymentViewSet(ModelViewSet):
    queryset = models.ListingPayment.objects.all()
    serializer_class = serializers.ListingPaymentSerializer

    def perform_create(self, serializer):
        promo = serializer.validated_data.get('promo_code', None)
        payment = serializer.save(user=self.request.user, status='pending', promo_code=promo)
        # Simulate or handle payment verification...
        payment.status = 'success'
        payment.save(update_fields=['status'])
        # On success, mark property as paid and set expiry
        prop = payment.property
        prop.expiry_date = timezone.now() + timezone.timedelta(days=14)
        prop.save(update_fields=['expiry_date'])




@api_view(['POST'])
def verify_listing_payment(request):
    reference = request.data.get("reference")
    if not reference:
        return Response({'error': 'Reference is required'}, status=400)

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
    except ValueError:
        return Response({'error': 'Invalid response from Paystack'}, status=502)

    if resp.status_code != 200 or not data.get('status'):
        return Response({'error': 'Verification failed', 'details': data}, status=400)

    tx = data['data']
    if tx.get('status') != 'success':
        return Response({'error': 'Payment not successful', 'details': tx.get('gateway_response')}, status=400)


    # At this point, Paystack says success
    try:
        payment = models.ListingPayment.objects.get(payment_ref=reference)
    except models.ListingPayment.DoesNotExist:
        return Response({'error': 'ListingPayment not found.'},
                        status=status.HTTP_404_NOT_FOUND)

    # Idempotency: if already handled
    if payment.status == 'success':
        return Response({'message': 'Already verified.'}, status=status.HTTP_200_OK)

    # 1) Mark payment successful
    payment.status = 'success'
    payment.save(update_fields=['status'])

    # 2) Publish the property
    prop = payment.property
    prop.is_verified = True
    prop.expiry_date = timezone.now() + timedelta(days=14)
    prop.save(update_fields=['is_verified', 'expiry_date'])

    return Response({'message': 'Listing payment verified and property published.'},
                    status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_subscription_payment(request):
    """
    POST /main/payments/verify-subscription/
    """
    print("🚀 VERIFY endpoint hit")
    reference = request.data.get("reference")
    if not reference:
        return Response({'error': 'Reference is required'}, status=400)

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        json_resp = resp.json()
    except requests.RequestException:
        logger.exception("Error contacting Paystack verify endpoint")
        return Response({'error': 'Error contacting Paystack.'}, status=502)

    # Check HTTP code & overall status
    if resp.status_code != 200 or not json_resp.get('status'):
        return Response({'error': 'Verification failed', 'details': json_resp}, status=400)

    tx = json_resp['data']
    if tx.get('status') != 'success':
        return Response({'error': 'Payment not successful', 'details': tx.get('gateway_response')}, status=400)

    # Fetch our payment record
    try:
        print(f"Looking for subscription payment with ref: {reference}")
        payment = models.SubscriptionPayment.objects.get(payment_ref=reference)
    except models.SubscriptionPayment.DoesNotExist:
        return Response({'error': 'SubscriptionPayment not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Idempotency
    if payment.status == 'success':
        return Response({'message': 'Already verified.'}, status=200)

    # 1) Mark payment successful
    payment.status = 'success'
    payment.save(update_fields=['status'])

    # 2) Activate or extend subscription
    sub = payment.subscription
    now = timezone.now()

    if sub.is_active and sub.end_date > now:
        sub.end_date += timedelta(days=sub.plan.duration_days)
    else:
        sub.start_date = now
        sub.end_date = now + timedelta(days=sub.plan.duration_days)
        sub.is_active = True

    sub.save(update_fields=['start_date', 'end_date', 'is_active'])

    return Response({'message': 'Subscription verified.'}, status=200)