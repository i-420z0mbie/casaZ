from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Max
from . filters import PropertyFilter 
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from . import models
from . import serializers


User = get_user_model()


class ProperyFeatureViewSet(ModelViewSet):
    queryset = models.PropertyFeature.objects.all()
    serializer_class = serializers.PropertyFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    


class PropertyViewSet(ModelViewSet):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'type', 'property_type']
    ordering_fields = ['price', 'date_posted', 'type', 'property_type']

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(creator=user)

    def perform_update(self, serializer):
        user = self.request.user

        if serializer.instance.creator != user:
            raise PermissionDenied({'Denied': 'You do not have the permission to edit this post!'})
        
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if instance.creator != user:
            raise PermissionDenied({'Denied': 'You do not have the permission to delete this post!'})
        
        instance.delete()

    
    @action(detail=False, methods=['get'], url_path='my-properties')
    def my_properties(self, request):
        user = request.user
        queryset = self.get_queryset().filter(creator=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PropertyImageViewSet(ModelViewSet):
    serializer_class = serializers.PropertyImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        property_pk = self.kwargs.get('property_pk')
        if property_pk:
            return models.PropertyImage.objects.filter(property_id=property_pk)
        return models.PropertyImage.objects.none() 

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        

        property_pk = self.kwargs.get('property_pk')
        if property_pk:
            context['property_id'] = property_pk
        
        return context
    
    def perform_create(self, serializer):
        property_id = self.kwargs['property_pk']
        user = self.request.user

 
        try:
            property_instance = models.Property.objects.get(pk=property_id)
        except models.Property.DoesNotExist:
            raise NotFound("Property does not exist.")

        if property_instance.creator != user:
            raise PermissionDenied("You do not have permission to add images to this property.")

        serializer.save(property=property_instance)

    
    def perform_destroy(self, instance):
        user = self.request.user
        property_instance = instance.property

        if property_instance.creator != user:
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
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def mark_read(self, request):
        ids = request.data.get('ids', [])
        models.Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
        return Response({'status': 'marked read'})
