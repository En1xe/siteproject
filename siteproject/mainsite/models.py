import os
import uuid
from datetime import timedelta

from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from moviepy.editor import VideoFileClip

VOTE_CHOICES = (
    ('like', 'Like'),
    ('dislike', 'Dislike'),
)

ACCESS_TYPE = (
    ('public', 'Публичный'),
    ('by_url', 'По ссылке'),
    ('limited', 'Ограниченный')
)


class VideoModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=1000, db_index=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user', db_index=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    access = models.CharField(choices=ACCESS_TYPE, max_length=100, default='public')
    file = models.FileField(upload_to='videos/')
    picture = models.ImageField(upload_to='pictures/')
    duration = models.PositiveIntegerField(help_text="Длительность видео в секундах", null=True, blank=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL для доступа к видео")

    def get_video_duration_in_seconds(self):
        # Используем абсолютный путь к файлу
        video_path = self.file.path  # Получаем путь к файлу

        if not os.path.exists(video_path):
            raise OSError(f"Файл {video_path} не найден!")

        # Извлечение длительности с использованием moviepy
        with VideoFileClip(video_path) as video:
            duration = video.duration
        return int(duration)


@receiver(pre_save, sender=VideoModel)
def set_video_duration(sender, instance, **kwargs):
    if not instance.duration and instance.file:
        video_path = instance.file.path
        if os.path.exists(video_path):
            with VideoFileClip(video_path) as video:
                instance.duration = int(video.duration)


class VoteModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.ForeignKey('VideoModel', on_delete=models.CASCADE, related_name='video_votes')
    creation_date = models.DateTimeField(auto_now_add=True)
    vote_type = models.CharField(choices=VOTE_CHOICES, max_length=7)

    class Meta:
        ordering = ['-creation_date']


class CommentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # Модель контента (PostModel или VideoModel)
    object_id = models.UUIDField(null=True)  # ID объекта, к которому привязывается комментарий
    content_object = GenericForeignKey('content_type', 'object_id')  # Устанавливает связь с объектом контента


class CommentsVoteModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=7, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.ForeignKey('CommentModel', on_delete=models.CASCADE, null=True)


class UserViewModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE, default=0)
    view_date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def can_add_view(user, video):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_view = UserViewModel.objects.filter(user=user, video=video, view_date__gte=one_hour_ago)
        return not recent_view.exists()


class SubscribeModel(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                               related_name='author')
    subscriber = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                   related_name='subscriber')

    class Meta:
        unique_together = ('author', 'subscriber')

    def clean(self):
        if self.author == self.subscriber:
            raise ValidationError(_('You cannot subscribe to yourself.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class PlayListModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='playlist_author')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='playlist_user', null=True)
    title = models.CharField(max_length=64)
    access = models.CharField(choices=ACCESS_TYPE, max_length=7, default='limited')
    creation_date = models.DateTimeField(auto_now_add=True)


class VideoPlayListModel(models.Model):
    video = models.ForeignKey('VideoModel', on_delete=models.CASCADE, related_name='video_playlists')
    playlist = models.ForeignKey('PlayListModel', on_delete=models.CASCADE, related_name='video_playlists')
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'playlist')


class PostsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts_author')
    text = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class PostsVoteModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.ForeignKey('PostsModel', on_delete=models.CASCADE, related_name='posts_votes', null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    vote_type = models.CharField(choices=VOTE_CHOICES, max_length=7)


class Feedback(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class PageVisit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.url} - {self.timestamp}"


class SearchRequests(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    request = models.CharField(max_length=256)
