from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.invitation.models import InvitationModel
from core.notification.models import NotificationModel


@receiver(post_save, sender=InvitationModel)
def create_notification_for_user(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        company = instance.company
        notification_text = f"New invitations from {company.name}"
        NotificationModel.objects.create(
            user=user,
            text=notification_text
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "message": notification_text,
            }
        )