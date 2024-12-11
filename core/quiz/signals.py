from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.notification.models import NotificationModel
from .models import QuizModel
from core.user.models import CustomUser


@receiver(post_save, sender=QuizModel)
def create_notification_for_user(sender, instance, created, **kwargs):
    if created:
        company = instance.company
        users = CustomUser.objects.filter(company=company)
        notification_text = f"New quiz from {company.name}"
        notifications = [NotificationModel(
            user=user,
            text=notification_text
        ) for user in users]
        NotificationModel.objects.bulk_create(notifications)

        channel_layer = get_channel_layer()
        for notification in notifications:
            async_to_sync(channel_layer.group_send)(
                f"user_{notification.user.id}",
                {
                    "type": "send_notification",
                    "message": notification.text,
                }
            )