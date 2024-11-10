from django.shortcuts import get_object_or_404
from .models import PageVisit, VideoModel
import re


import re
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import PageVisit, VideoModel

class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Проверяем, является ли текущий URL страницей видео
        match = re.match(r'^/watch/(?P<uuid>[0-9a-fA-F-]+)', request.path)
        if match and request.user.is_authenticated:  # Проверяем, что пользователь авторизован
            video_uuid = match.group('uuid')

            # Ищем видео по UUID
            video = get_object_or_404(VideoModel, id=video_uuid)

            # Обновляем запись посещения или создаём новую, если не существует
            page_visit, created = PageVisit.objects.get_or_create(
                user=request.user,
                video=video,
                defaults={'timestamp': timezone.now()}
            )

            # Если запись уже существует, обновляем время просмотра
            if not created:
                page_visit.timestamp = timezone.now()
                page_visit.save()

        return response

