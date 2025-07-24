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
# signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Property, Notification, ListingPayment

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


# main/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, PushToken
from .expo_utils import send_expo_push

@receiver(post_save, sender=Message)
def send_message_push(sender, instance: Message, created, **kwargs):
    if not created:
        return

    print(f"[DEBUG] post_save for Message {instance.id} (from {instance.sender} to {instance.recipient})")

    tokens = list(
        PushToken.objects.filter(user=instance.recipient).values_list('token', flat=True)
    )
    print(f"[DEBUG] Found tokens: {tokens}")

    title = f"New message from {instance.sender.username}"
    body  = instance.content[:100]

    for t in tokens:
        try:
            print(f"[DEBUG] Sending push to {t} …")
            result = send_expo_push(t, title, body, data={'chatId': str(instance.id)})
            print(f"[DEBUG] Expo response: {result}")
        except Exception as exc:
            print(f"[ERROR] send_expo_push failed for {t}: {exc}")



@receiver(post_save, sender=Notification)
def send_notification_push(sender, instance: Notification, created, **kwargs):
    if not created:
        return

    print(f"[DEBUG] post_save for Notification {instance.id} (type={instance.notif_type}) to {instance.user}")
    tokens = list(
        PushToken.objects.filter(user=instance.user).values_list('token', flat=True)
    )
    print(f"[DEBUG] Found tokens: {tokens}")

    # Craft a human‑friendly title/body for your notif_type
    if instance.notif_type == Notification.NOTIF_VERIFIED:
        title = "Your property was verified ✅"
        body  = "Congratulations—one of your listings just got verified!"
    elif instance.notif_type == Notification.NOTIF_FAVORITE:
        title = "Someone favorited your property ❤️"
        body  = "A user just added one of your listings to their favorites."
    else:
        title = "You have a new notification"
        body  = ""

    for t in tokens:
        try:
            print(f"[DEBUG] Sending push to {t} …")
            result = send_expo_push(t, title, body, data={'notifId': str(instance.id)})
            print(f"[DEBUG] Expo response: {result}")
        except Exception as exc:
            print(f"[ERROR] send_expo_push failed for {t}: {exc}")






@receiver(pre_save, sender=ListingPayment)
def _capture_old_status(sender, instance, **kwargs):
    """
    Before saving, stash the old status on the instance so we can compare in post_save.
    """
    if not instance.pk:
        instance._old_status = None
    else:
        old = sender.objects.get(pk=instance.pk)
        instance._old_status = old.status

@receiver(post_save, sender=ListingPayment)
def _notify_admin_on_success(sender, instance, created, **kwargs):
    """
    After saving, if status just turned to 'success', send an email to the admin.
    """
    # Did it just become successful?
    became_success = (
        (created and instance.status == 'success')
        or
        (not created and instance.status == 'success' and instance._old_status != 'success')
    )
    if not became_success:
        return

    subject = "✅ New Listing Payment Verified"
    message = (
        f"User: {instance.user.email}  \n"
        f"Property ID: {instance.property.id}  \n"
        f"Amount: {instance.amount}  \n"
        f"Promo code: {instance.promo_code or '—'}  \n"
        f"Reference: {instance.payment_ref}"
    )

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if not admin_email:

        admin_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )