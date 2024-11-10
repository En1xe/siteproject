import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count, ExpressionWrapper, F, IntegerField, QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import DownloadForm, CommentForm, PlaylistForm, PostForm, FeedbackForm
from .funcs import handle_vote, vote_on_comment, handle_subscription_action
from .models import VideoModel, SubscribeModel, VoteModel, UserViewModel, CommentModel, PostsVoteModel, PlayListModel, \
    VideoPlayListModel, PostsModel, PageVisit, SearchRequests
from moviepy.editor import VideoFileClip

class SearchResultsView(LoginRequiredMixin, ListView):
    model = VideoModel
    template_name = 'mainsite/search_results.html'
    context_object_name = 'content'

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        filter_by = self.request.GET.get('filter_by', 'all')  # Параметры фильтрации
        type_filter = self.request.GET.get('type_filter', 'all')
        duration_filter = self.request.GET.get('duration_filter', 'all')
        sort_by = self.request.GET.get('sort_by', 'date')

        # Начальные запросы для всех моделей
        video_results = VideoModel.objects.all()
        user_results = get_user_model().objects.all()
        playlist_results = PlayListModel.objects.all()

        # Фильтрация по запросу
        if query:
            if not SearchRequests.objects.filter(request=query, user=self.request.user).exists():
                SearchRequests.objects.create(request=query, user=self.request.user)

            video_results = video_results.filter(Q(title__icontains=query) | Q(description__icontains=query))
            user_results = user_results.filter(Q(username__icontains=query) | Q(alias__icontains=query))
            playlist_results = playlist_results.filter(Q(title__icontains=query))

        # Фильтрация по дате
        if filter_by == 'hour':
            last_hour = timezone.now() - timedelta(hours=1)
            video_results = video_results.filter(creation_date__gte=last_hour)
            user_results = user_results.filter(date_joined__gte=last_hour)
        elif filter_by == 'today':
            today = timezone.now().date()
            video_results = video_results.filter(creation_date__date=today)
        elif filter_by == 'week':
            week_start = timezone.now() - timedelta(weeks=1)
            video_results = video_results.filter(creation_date__gte=week_start)
        elif filter_by == 'month':
            month_start = timezone.now() - timedelta(days=30)
            video_results = video_results.filter(creation_date__gte=month_start)
        elif filter_by == 'year':
            year_start = timezone.now() - timedelta(days=365)
            video_results = video_results.filter(creation_date__gte=year_start)

        # Фильтрация по длительности (только для видео)
        if type_filter == 'video' and duration_filter:
            if duration_filter == 'short':
                video_results = video_results.filter(duration__lt=240)  # Менее 4 минут
            elif duration_filter == 'medium':
                video_results = video_results.filter(duration__gte=240, duration__lte=1200)  # От 4 до 20 минут
            elif duration_filter == 'long':
                video_results = video_results.filter(duration__gt=1200)  # Более 20 минут

        # Фильтрация по типу
        if type_filter != 'all':
            if type_filter == 'video':
                user_results = []
                playlist_results = []
            elif type_filter == 'user':
                video_results = []
                playlist_results = []
            elif type_filter == 'playlist':
                video_results = []
                user_results = []

        # Сортировка (применяется только к QuerySet, а не спискам)
        if sort_by == 'date':
            if isinstance(video_results, QuerySet):
                video_results = video_results.order_by('-creation_date')
        elif sort_by == 'rating':
            if isinstance(video_results, QuerySet):
                video_results = video_results.annotate(
                    likes=Count('video_votes', filter=Q(video_votes__vote_type='like')),
                    dislikes=Count('video_votes', filter=Q(video_votes__vote_type='dislike'))
                ).annotate(
                    rating=ExpressionWrapper(F('likes') - F('dislikes'), output_field=IntegerField())
                ).order_by('-rating')
        elif sort_by == 'views':
            if isinstance(video_results, QuerySet):
                video_results = video_results.annotate(num_views=Count('pagevisit')).order_by('-num_views')

        # Объединение всех результатов
        results = []
        if isinstance(video_results, QuerySet) and video_results.exists():
            results.extend([{'type': 'video', 'item': video} for video in video_results])
        if isinstance(user_results, QuerySet) and user_results.exists():
            results.extend([{'type': 'user', 'item': user} for user in user_results])
        if isinstance(playlist_results, QuerySet) and playlist_results.exists():
            results.extend([{'type': 'playlist', 'item': playlist} for playlist in playlist_results])

        return results

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('mainsite/search_results_part.html', context, request=self.request)
            return JsonResponse({'html': html})
        else:
            return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        context['query'] = query  # Передаем запрос в контекст
        context['filter_by'] = self.request.GET.get('filter_by', 'all')
        context['type_filter'] = self.request.GET.get('type_filter', 'all')
        context['duration_filter'] = self.request.GET.get('duration_filter', 'all')
        context['sort_by'] = self.request.GET.get('sort_by', 'date')
        return context


    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type')

        if action_type in ['subscribe', 'unsubscribe']:
            return handle_subscription_action(request)

        return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def search_history(request):
    history = SearchRequests.objects.filter(user=request.user).order_by('-creation_date')[:10]
    data = {
        'history': [{'id': item.id, 'query': item.request} for item in history]
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
def delete_query(request, request_id):
    if request.method == 'POST':
        # Получаем объект запроса по request_id, переданному в URL
        query = get_object_or_404(SearchRequests, id=request_id, user=request.user)

        # Удаляем запрос
        query.delete()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


class BaseFeedbackView(View):
    form_class = FeedbackForm
    template_name = 'mainsite/feedback.html'


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return JsonResponse({'success': True, 'message': 'Спасибо за ваш отзыв!'})
        return JsonResponse({'success': False, 'errors': form.errors})


class HomePage(ListView, BaseFeedbackView):
    model = VideoModel
    template_name = 'mainsite/homepage.html'
    context_object_name = 'videos'

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_form'] = self.form_class()  # Создайте экземпляр формы и добавьте в контекст
        return context


class SubscriptionsContent(LoginRequiredMixin, ListView, BaseFeedbackView):
    template_name = 'mainsite/subscribe_content.html'
    model = VideoModel
    context_object_name = 'videos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()  # Создайте экземпляр формы и добавьте в контекст
        authors = SubscribeModel.objects.filter(subscriber=self.request.user).values_list('author', flat=True)
        context['subscribe_videos'] = VideoModel.objects.filter(user__in=authors).order_by('creation_date')
        return context

class DetailPostsView(DetailView, BaseFeedbackView):
    template_name = 'mainsite/detail_post.html'
    model = PostsModel
    slug_field = 'id'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        content_type = ContentType.objects.get_for_model(PostsModel)
        alias_dict = {comment.user.username: comment.user.alias
                      for comment in CommentModel.objects.filter(content_type=content_type, object_id=post.id)}

        context['alias_dict'] = alias_dict
        context['comment_form'] = CommentForm()
        context['reply_form'] = CommentForm()
        context['post'] = post
        context['comments'] = CommentModel.objects.filter(Q(object_id=post.id) & Q(parent__isnull=True)).order_by('-creation_date')
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type')
        post = self.get_object()
        post_content_type = ContentType.objects.get_for_model(PostsModel)
        comment_form = CommentForm(request.POST)
        reply_form = CommentForm(request.POST)

        if comment_form.is_valid() and not request.POST.get('parent_id'):
            comment = comment_form.save(commit=False)
            comment.object_id = post.id
            comment.content_type = post_content_type
            comment.user = request.user
            comment.save()
            return redirect('detail_post', uuid=post.id)

        elif reply_form.is_valid() and request.POST.get('parent_id'):
            parent_id = request.POST.get('parent_id')
            parent_comment = get_object_or_404(CommentModel, id=parent_id)
            reply = reply_form.save(commit=False)
            reply.object_id = post.id
            reply.content_type = post_content_type
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
            return redirect('detail_post', uuid=post.id)

        elif action_type in ['like', 'dislike']:
            return handle_vote(request, post, action_type, PostsVoteModel)

        elif action_type == 'like_comment' or action_type == 'dislike_comment':
            comment_id = request.POST.get('comment_id')
            vote_type = 'like' if action_type == 'like_comment' else 'dislike'
            return vote_on_comment(request, comment_id, vote_type)


class HomePlaylistView(LoginRequiredMixin, ListView, BaseFeedbackView):
    template_name = 'mainsite/home_playlists.html'
    model = PlayListModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.request.GET.get('list')

        if playlist:
            context['playlist'] = PlayListModel.objects.get(id=playlist)
            context['playlist_videos'] = VideoPlayListModel.objects.filter(playlist=playlist)
        context['playlists'] = PlayListModel.objects.filter(user=self.request.user)
        return context


class CreatePostView(LoginRequiredMixin, CreateView, BaseFeedbackView):
    template_name = 'mainsite/create_post.html'
    model = PostsModel
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        postform = PostForm(request.POST, request.FILES)
        if postform.is_valid():
            post = postform.save(commit=False)
            post.author = self.request.user
            post.save()
            return redirect('homepage')
        else:
            # Обработка ошибок формы
            return self.form_invalid(postform)


class DownloadView(LoginRequiredMixin, CreateView):
    template_name = 'mainsite/download_video.html'
    form_class = DownloadForm
    model = VideoModel
    success_url = reverse_lazy('homepage')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        video_instance = self.object
        video_file_path = os.path.join(settings.MEDIA_ROOT, video_instance.file.name)

        if not os.path.exists(video_file_path):
            raise OSError(f"Файл {video_file_path} не найден!")

        try:
            with VideoFileClip(video_file_path) as video:
                duration = video.duration
                video_instance.duration = int(duration)
                video_instance.save()
        except Exception:
            raise

        return response


class DetailVideoView(DetailView, BaseFeedbackView):
    template_name = 'mainsite/watch_video.html'
    context_object_name = 'video'
    model = VideoModel
    slug_field = 'id'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object.user
        content_type = ContentType.objects.get_for_model(VideoModel)
        video = self.get_object()
        comments = CommentModel.objects.filter(content_type=content_type, object_id=video.id, parent__isnull=True).order_by('-creation_date')
        alias_dict = {comment.user.username: comment.user.alias
                      for comment in CommentModel.objects.filter(content_type=content_type, object_id=video.id)}

        if self.request.user.is_authenticated:
            context['is_subscribed'] = SubscribeModel.objects.filter(
                subscriber=self.request.user,
                author=author
            ).exists()

        user_vote = VoteModel.objects.filter(user=self.request.user, content=video).first()
        context['user_vote_type'] = user_vote.vote_type if user_vote else None


        playlist = self.request.GET.get('list')
        if playlist:
            playlist_videos = VideoPlayListModel.objects.filter(playlist=playlist).order_by('-creation_date')
            index = 1
            for vid in playlist_videos.order_by('-creation_date'):
                if vid.video == self.object:
                    context['video_index'] = index
                    break
                index += 1

            context['playlist_videos'] = playlist_videos
            context['playlist'] = PlayListModel.objects.get(id=playlist)
            context['num_of_pl_videos'] = playlist_videos.count()

        context['video_playlists'] = VideoPlayListModel.objects.filter(video=self.object).values_list('playlist_id', flat=True)
        context['playlists'] = PlayListModel.objects.filter(user=self.request.user)
        context['author'] = author
        context['comment_form'] = CommentForm()
        context['reply_form'] = CommentForm()
        context['playlist_form'] = PlaylistForm()
        context['comments'] = comments
        context['alias_dict'] = alias_dict
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        video = self.get_object()
        action_type = request.POST.get('action_type')
        comment_form = CommentForm(request.POST)
        reply_form = CommentForm(request.POST)
        playlist_form = PlaylistForm(request.POST)
        playlists = request.POST.getlist('playlists')
        content_type = ContentType.objects.get_for_model(VideoModel)

        if playlist_form.is_valid():
            playlist = playlist_form.save(commit=False)
            playlist.title = request.POST.get('title')
            playlist.author = self.request.user
            playlist.user = self.request.user
            playlist.access = request.POST.get('access')
            playlist.save()
            VideoPlayListModel.objects.create(video=video, playlist=playlist)
            return redirect('detail_video', uuid=video.id)

        if comment_form.is_valid() and not request.POST.get('parent_id'):
            comment = comment_form.save(commit=False)
            comment.content_type = content_type
            comment.object_id = video.id
            comment.user = request.user
            comment.save()
            return redirect('detail_video', uuid=video.id)

        elif reply_form.is_valid() and request.POST.get('parent_id'):
            parent_id = request.POST.get('parent_id')
            parent_comment = get_object_or_404(CommentModel, id=parent_id)
            reply = reply_form.save(commit=False)
            reply.content_type = content_type
            reply.object_id = video.id
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
            return redirect('detail_video', uuid=video.id)

        elif action_type == 'add_to_playlists' and playlists:
            for playlist_id in playlists:
                playlist = get_object_or_404(PlayListModel, id=playlist_id)
                if not VideoPlayListModel.objects.filter(video=video, playlist=playlist).exists():
                    VideoPlayListModel.objects.create(video=video, playlist=playlist)
            return JsonResponse({'message': 'Видео добавлено в выбранные плейлисты.'})

        elif action_type == 'remove_from_playlists' and playlists:
            for playlist_id in playlists:
                playlist = get_object_or_404(PlayListModel, id=playlist_id)
                deleted_count, _ = VideoPlayListModel.objects.filter(video=video, playlist=playlist).delete()
            return JsonResponse({'message': 'Видео удалено из выбранных плейлистов.'})

        elif action_type in ['subscribe', 'unsubscribe']:
            return handle_subscription_action(request)

        elif action_type in ['like', 'dislike']:
            return handle_vote(request, video, action_type, VoteModel)

        if action_type == 'like_comment' or action_type == 'dislike_comment':
            comment_id = request.POST.get('comment_id')
            return vote_on_comment(request, comment_id, action_type.split('_')[0])

        elif action_type == 'view':
            return self.track_view(request, video)

        return JsonResponse({'error': 'Invalid action'}, status=400)


    def track_view(self, request, video):
        """Метод для учёта просмотров"""
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=403)

        video_duration = video.get_video_duration_in_seconds()
        current_watch_time = float(request.POST.get('current_time', 0))

        if video_duration <= 60:
            min_watch_time = video_duration * 0.1
        else:
            min_watch_time = video_duration * 0.01

        if current_watch_time >= min_watch_time and UserViewModel.can_add_view(request.user, video):
            UserViewModel.objects.create(user=request.user, video=video)
            return JsonResponse({'status': 'viewed'})

        return JsonResponse({'status': 'not viewed'}, status=400)


class HistoryView(LoginRequiredMixin, ListView, BaseFeedbackView):
    template_name = 'mainsite/history.html'
    model = PageVisit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = PageVisit.objects.filter(user=self.request.user).select_related('video')
        context['videos'] = videos
        return context


class DeleteHistoryView(View):
    def post(self, request, visit_id):
        if request.user.is_authenticated:
            page_visit = get_object_or_404(PageVisit, id=visit_id, user=request.user)
            page_visit.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=400)


class LikedVideosView(LoginRequiredMixin, ListView, BaseFeedbackView):
    template_name = 'mainsite/liked_content.html'
    model = VoteModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = VoteModel.objects.filter(user=self.request.user, vote_type='like').values_list('content', flat=True)
        context['videos'] = VideoModel.objects.filter(id__in=videos)
        return context


@method_decorator(csrf_exempt, name='dispatch')
class DeleteLikeView(View):
    def post(self, request, uuid):
        vote = get_object_or_404(VoteModel, user=request.user, content__id=uuid, vote_type='like')
        vote.delete()
        return JsonResponse({'success': True})

    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'}, status=400)

