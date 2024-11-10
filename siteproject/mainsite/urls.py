from django.urls import path, register_converter

from .converter import AliasConverter
from .views import HomePage, DownloadView, SearchResultsView, DetailVideoView, HomePlaylistView, CreatePostView, \
    DetailPostsView, BaseFeedbackView, SubscriptionsContent, HistoryView, DeleteHistoryView, LikedVideosView, \
    DeleteLikeView, search_history, delete_query

register_converter(AliasConverter, 'alias')

urlpatterns = [
    path('', HomePage.as_view(), name='homepage'),
    path('download/', DownloadView.as_view(), name='download'),
    path('results', SearchResultsView.as_view(), name='results'),
    path('watch/<uuid:uuid>', DetailVideoView.as_view(), name='detail_video'),
    path('playlists', HomePlaylistView.as_view(), name='home_playlists'),
    path('community', CreatePostView.as_view(), name='create_post'),
    path('community/<uuid:uuid>', DetailPostsView.as_view(), name='detail_post'),
    path('submit-feedback/', BaseFeedbackView.as_view(), name='submit_feedback'),
    path('subscriptions', SubscriptionsContent.as_view(), name='subscriptions'),
    path('history', HistoryView.as_view(), name='history'),
    path('delete-history/<int:visit_id>/', DeleteHistoryView.as_view(), name='delete_history'),
    path('liked_content', LikedVideosView.as_view(), name='liked_content'),
    path('delete-like/<uuid:uuid>/', DeleteLikeView.as_view(), name='delete_like'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('search-history/', search_history, name='search_history'),
    path('delete_query/<int:request_id>/', delete_query, name='delete_query'),
]