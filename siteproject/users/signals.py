from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=get_user_model())
def delete_related_data(sender, instance, **kwargs):
    # Удаляем связанные данные
    if hasattr(instance, 'profile'):  # Проверяем, существует ли профиль
        instance.profile.delete()  # Удаляем профиль