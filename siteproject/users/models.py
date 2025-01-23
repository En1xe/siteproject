import random
import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def generate_key(length=16):
    characters = string.ascii_letters + string.digits + '-_'
    while True:
        key = ''.join(secrets.choice(characters) for _ in range(length))
        if not get_user_model().objects.filter(alias=key).exists():
            return '@' + key

class User(AbstractUser):
    banner = models.ImageField(upload_to='banners/', default='default_banner/default_banner.png', blank=True)
    user_icon = models.ImageField(upload_to='icons/', default='default_icon/user_icon.png', blank=True)
    channel_description = models.TextField(max_length=1500, blank=True)
    alias = models.CharField(max_length=17, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = generate_key()
        super().save(*args, **kwargs)

    def is_default_field(self, field):
        return self.banner.name == 'default_banner/default_banner.png' if field == 'banner' \
        else self.user_icon.name == 'default_icon/user_icon.png'


class SecurityCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    new_email = models.EmailField(null=True, blank=True)

    @staticmethod
    def generate_code():
        from django.utils.crypto import get_random_string
        return get_random_string(length=6, allowed_chars='0123456789')

    def is_valid(self):
        """Проверяет, не истек ли срок действия кода."""
        from django.utils.timezone import now
        return now() <= self.expiration_time

