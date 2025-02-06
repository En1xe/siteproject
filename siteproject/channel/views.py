import os

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView

from channel.forms import EditContentForm, EditPostForm
from mainsite.funcs import handle_vote, handle_subscription_action
from mainsite.models import SubscribeModel, VideoModel, PlayListModel, PostsVoteModel, PostsModel


class ChannelView(LoginRequiredMixin, DetailView):
    template_name = 'channel/channel.html'
    model = get_user_model()
    context_object_name = 'author'  # Так автор будет доступен в шаблоне как {{ author }}

    def get_object(self, queryset=None):
        # Переопределяем метод для поиска объекта по alias
        alias = self.kwargs.get('alias')  # Извлекаем alias из URL
        return get_object_or_404(get_user_model(), alias=alias)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object  # Автор берется из get_object()

        if self.request.user.is_authenticated:
            context['is_subscribed'] = SubscribeModel.objects.filter(
                subscriber=self.request.user,
                author=author
            ).exists()

        context['author'] = author
        context['subscribers'] = SubscribeModel.objects.filter(author=author).count()
        return context

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type')
        if action_type in ['subscribe', 'unsubscribe']:
            return handle_subscription_action(request)
        return JsonResponse({'error': 'Invalid action'}, status=400)

class ChannelVideoView(ChannelView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_user_model().objects.get(alias=self.kwargs.get('alias'))

        context['channel_content_type'] = 'videos'
        context['videos'] = VideoModel.objects.filter(user=author)
        return context

class ChannelPlaylistView(ChannelView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_user_model().objects.get(alias=self.kwargs.get('alias'))

        context['channel_content_type'] = 'playlists'
        context['playlists'] = PlayListModel.objects.filter(author=author)
        return context


class ChannelCommunityView(ChannelView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['channel_content_type'] = 'posts'
        context['votemodel'] = PostsVoteModel
        context['posts'] = PostsModel.objects.filter(author=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type')
        post = PostsModel.objects.get(id=request.POST.get('post'))

        if action_type in ['like', 'dislike']:
            return handle_vote(request, post, action_type, PostsVoteModel)


class ChannelSubscriptionView(ChannelView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_content_type'] = 'subscription'
        return context


class ListContentVideo(LoginRequiredMixin, ListView):
    template_name = 'channel/list_content_videos.html'
    model = VideoModel
    paginate_by = 5
    context_object_name = 'videos'

    def get(self, request, *args, **kwargs):
        url_alias = self.kwargs.get('alias')
        if str(request.user.alias) != str(url_alias):
            return redirect('list_content_video', alias=request.user.alias)
        return super().get(request, *args, **kwargs)\

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type', '')
        content_id = request.POST.get('content_id', '')

        if action_type == 'delete-content':
            video = get_object_or_404(VideoModel, id=content_id)
            video.delete()
            return JsonResponse({'status': 'success'})


    def get_queryset(self):
        return VideoModel.objects.filter(user=self.request.user)


class ListContentPosts(ListView):
    template_name = 'channel/list_content_posts.html'
    model = PostsModel
    paginate_by = 5
    context_object_name = 'posts'

    def get(self, request, *args, **kwargs):
        url_alias = self.kwargs.get('alias')
        if str(request.user.alias) != str(url_alias):
            return redirect('list_content_post', alias=request.user.alias)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type', '')
        content_id = request.POST.get('content_id', '')

        if action_type == 'delete-content':
            video = get_object_or_404(PostsModel, id=content_id)
            video.delete()
            return JsonResponse({'status': 'success'})

    def get_queryset(self):
        return PostsModel.objects.filter(author=self.request.user)


class EditVideo(UpdateView):
    template_name = 'channel/edit_video.html'
    model = VideoModel
    form_class = EditContentForm
    slug_field = 'id'
    slug_url_kwarg = 'uuid'
    context_object_name = 'video'
    success_url = reverse_lazy('list_content_video', kwargs={'alias': get_user_model().alias})

    def get(self, request, *args, **kwargs):
        url_alias = self.kwargs.get('alias')
        if str(request.user.alias) != str(url_alias):
            return redirect('list_content_video', alias=request.user.alias)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object
        context['video_file_name'] = os.path.basename(video.file.name)
        return context


class EditPost(UpdateView):
    template_name = 'channel/edit_post.html'
    model = PostsModel
    form_class = EditPostForm
    slug_field = 'id'
    slug_url_kwarg = 'uuid'
    context_object_name = 'post'
    success_url = reverse_lazy('list_content_post', kwargs={'alias': get_user_model().alias})

    def get(self, request, *args, **kwargs):
        url_alias = self.kwargs.get('alias')
        if str(request.user.alias) != str(url_alias):
            return redirect('list_content_post', alias=request.user.alias)
        return super().get(request, *args, **kwargs)


