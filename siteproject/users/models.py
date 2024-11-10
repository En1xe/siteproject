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

    def is_default_banner(self):
        return self.banner and self.banner.name == 'default_banner/default_banner.png'

    def is_default_user_icon(self):
        return self.user_icon and self.user_icon.name == 'default_icon/user_icon.png'


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expiration_time

    @staticmethod
    def generate_code():
        return f"{random.randint(100000, 999999)}"

