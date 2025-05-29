# signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Property, Notification

channel_layer = get_channel_layer()

@receiver(pre_save, sender=Property)
def cache_old_verification(sender, instance, **kwargs):
    # stash the old is_verified for comparison in post_save
    if instance.pk:
        try:
            old = Property.objects.get(pk=instance.pk)
            instance._old_is_verified = old.is_verified
        except Property.DoesNotExist:
            instance._old_is_verified = False
    else:
        instance._old_is_verified = False

@receiver(post_save, sender=Property)
def property_verified(sender, instance, created, **kwargs):
    # if not newly created, and was False → now True, send notification
    if not created and not getattr(instance, '_old_is_verified', False) and instance.is_verified:
        notif = Notification.objects.create(
            user=instance.creator,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            notif_type=Notification.NOTIF_VERIFIED
        )
        data = {
            'id': str(notif.id),
            'user': notif.user.id,
            'notif_type': notif.notif_type,
            'object_id': str(notif.object_id),
            'object_data': {'title': instance.title, 'slug': instance.slug},
            'timestamp': notif.timestamp.isoformat(),
            'is_read': notif.is_read,
        }
        async_to_sync(channel_layer.group_send)(
            f'notifications_{instance.creator.id}',
            {'type': 'notify', 'data': data}
        )
