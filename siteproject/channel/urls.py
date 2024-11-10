from django.urls import path, register_converter

from mainsite.converter import AliasConverter
from .views import ChannelView, ChannelVideoView, ChannelPlaylistView, ChannelCommunityView, \
    ChannelSubscriptionView, ListContentVideo, EditVideo, ListContentPosts, EditPost

register_converter(AliasConverter, 'alias')

urlpatterns = [
    path('<alias>', ChannelView.as_view(), name='channel'),
    path('<alias>/videos', ChannelVideoView.as_view(), name='channel_videos'),
    path('<alias>/playlists', ChannelPlaylistView.as_view(), name='channel_playlists'),
    path('<alias>/community', ChannelCommunityView.as_view(), name='channel_community'),
    path('<alias>/subscription', ChannelSubscriptionView.as_view(), name='channel_subscription'),
    path('<alias>/content_video', ListContentVideo.as_view(), name='list_content_video'),
    path('<alias>/content_post', ListContentPosts.as_view(), name='list_content_post'),
    path('<alias>/content_video/<uuid:uuid>', EditVideo.as_view(), name='edit_video'),
    path('<alias>/content_post/<uuid:uuid>', EditPost.as_view(), name='edit_post'),
]