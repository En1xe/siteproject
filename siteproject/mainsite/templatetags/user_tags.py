import re
from datetime import datetime, timezone
from django import template
from django.contrib.auth import get_user_model
from django.core.exceptions import ViewDoesNotExist

from mainsite.models import VideoPlayListModel, PostsVoteModel, CommentsVoteModel, VoteModel, SubscribeModel, \
    UserViewModel, CommentModel, ACCESS_TYPE

register = template.Library()

months_in_genitive = {
    1: "Января",
    2: "Февраля",
    3: "Марта",
    4: "Апреля",
    5: "Мая",
    6: "Июня",
    7: "Июля",
    8: "Августа",
    9: "Сентября",
    10: "Октября",
    11: "Ноября",
    12: "Декабря",
}

@register.filter
def get_profile_image(user):
    return user.user_icon.url if user.user_icon else '/media/default_icon/user_icon.png'


@register.simple_tag
def get_last_video(playlist):
    try:
        last_video_play = VideoPlayListModel.objects.filter(playlist=playlist).latest('creation_date')
        return last_video_play.video
    except VideoPlayListModel.DoesNotExist:
        return None

@register.simple_tag
def comments_total_likes(content):
    return CommentsVoteModel.objects.filter(vote_type='like', content=content).count()

@register.simple_tag
def comments_total_dislikes(content):
    return CommentsVoteModel.objects.filter(vote_type='dislike', content=content).count()

@register.simple_tag
def content_total_likes(content, type):
    if type == 'video':
        return VoteModel.objects.filter(vote_type='like', content=content).count()
    elif type == 'post':
        return PostsVoteModel.objects.filter(vote_type='like', content=content).count()

@register.simple_tag
def content_total_dislikes(content, type):
    if type == 'video':
        return VoteModel.objects.filter(vote_type='dislike', content=content).count()
    elif type == 'post':
        return PostsVoteModel.objects.filter(vote_type='dislike', content=content).count()

@register.simple_tag
def list_of_subs(user):
    return SubscribeModel.objects.filter(subscriber=user)

@register.simple_tag
def get_views(video):
    return UserViewModel.objects.filter(video=video).count()

@register.simple_tag
def get_comments(video):
    return CommentModel.objects.filter(object_id=video.id).count()

@register.simple_tag
def get_video_percent(video):
    likes = VoteModel.objects.filter(content=video, vote_type='like').count()
    dislikes = VoteModel.objects.filter(content=video, vote_type='dislike').count()
    total_votes = likes + dislikes
    return f'{likes / total_votes * 100:.1f} %' if total_votes > 0 else '-'

@register.simple_tag
def get_post_percent(post):
    likes = PostsVoteModel.objects.filter(content=post, vote_type='like').count()
    dislikes = PostsVoteModel.objects.filter(content=post, vote_type='dislike').count()
    total_votes = likes + dislikes
    return f'{likes / total_votes * 100:.1f} %' if total_votes > 0 else '-'

@register.filter
def get_date(creation_date):
    cur_date = datetime.now(timezone.utc)
    time_diff = cur_date - creation_date.replace(tzinfo=timezone.utc)
    diff_in_sec = round(time_diff.total_seconds())
    if diff_in_sec // 60 == 0:
        if diff_in_sec == 1: return f'{diff_in_sec} секунду назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} секунды назад'
        else: return f'{diff_in_sec} секунд назад'
    elif diff_in_sec // 3600 == 0:
        diff_in_sec //= 60
        if diff_in_sec == 1: return f'{diff_in_sec} минуту назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} минуты назад'
        else: return f'{diff_in_sec} минут назад'
    elif diff_in_sec // 86400 == 0:
        diff_in_sec //= 3600
        if diff_in_sec == 1: return f'{diff_in_sec} час назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} часа назад'
        else: return f'{diff_in_sec} часов назад'
    elif diff_in_sec // 604800 == 0:
        diff_in_sec //= 86400
        if diff_in_sec == 1: return f'{diff_in_sec} день назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} дня назад'
        else: return f'{diff_in_sec} дней назад'
    elif diff_in_sec // 2592000 == 0:
        diff_in_sec //= 604800
        if diff_in_sec == 1: return f'{diff_in_sec} неделю назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} недели назад'
        else: return f'{diff_in_sec} недель назад'
    elif diff_in_sec // 31104000 == 0:
        diff_in_sec //= 2592000
        if diff_in_sec == 1: return f'{diff_in_sec} месяц назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} месяца назад'
        else: return f'{diff_in_sec} месяцев назад'
    elif diff_in_sec // 31104000 > 0:
        diff_in_sec //= 31104000
        if diff_in_sec == 1: return f'{diff_in_sec} год назад'
        elif 1 < diff_in_sec < 5: return f'{diff_in_sec} года назад'
        else: return f'{diff_in_sec} лет назад'
    else:
        return None

@register.filter
def get_rel_views(video):
    views = get_views(video)

    if views == 1:
        word = 'просмотр'
    elif 1 < views < 5:
        word = 'просмотра'
    else:
        word = 'просмотров'

    if 1000 <= views < 1000000:
        views /= 1000
    elif views >= 1000000:
        views /= 1000000

    return f'{views:.0f} {word}'.replace('.', ',')


@register.filter
def get_video_duration(duration):
    # Проверяем, что duration не None и не пустая строка
    if duration is None or duration == '':
        return "Длительность не указана"  # Возвращаем сообщение о недоступной длительности

    try:
        # Преобразуем duration в int
        duration = int(duration)  # Здесь может возникнуть ошибка ValueError, если не числовое значение
    except (ValueError, TypeError):
        return "Неверная длительность"  # Возвращаем сообщение о неверной длительности

    hours = duration // 3600
    minutes = (duration % 3600) // 60
    remaining_seconds = duration % 60

    if hours > 0:
        return f"{hours}:{minutes:02}:{remaining_seconds:02}"
    else:
        return f"{minutes}:{remaining_seconds:02}"

@register.filter
def get_access_name(access):
    access_type = dict(ACCESS_TYPE)
    return access_type[access]

@register.filter
def get_date_name(date):
    day = date.day
    month = months_in_genitive[date.month]
    year = date.year
    return f'{day} {month} {year} г.'

@register.filter
def get_subs(author):
    num = SubscribeModel.objects.filter(author=author).count()
    if num == 1:
        return f'{num} подписчик'
    elif 1 < num < 5:
        return f'{num} подписчикa'
    elif num % 999 == 0:
        return f'{num} подписчиков'
    elif num % 999999 == 0:
        return f'{num} тыс. подписчик'
    elif num % 999999 > 0:
        return f'{num} млн.подписчик'

@register.filter
def get_comments_name(content):
    comm_count = get_comments(content)
    if not comm_count:
        return f'Нет комментариев'
    elif comm_count == 1:
        return f'{comm_count} комментарий'
    elif 1 < comm_count < 5:
        return f'{comm_count} комментария'
    elif 4 < comm_count < 1000000:
        return f'{comm_count} комментариев'
    elif comm_count > 999999:
        return f'{comm_count/1000000:.1f} млн. комментариев'


@register.filter(name='mention_to_link')
def mention_to_link(value, alias_dict):
    """
    Преобразует @username в ссылку на профиль пользователя с использованием alias,
    только если пользователь существует в базе данных с таким alias.
    """

    def replace_with_link(match):
        username = match.group(1)

        # Получаем alias пользователя из alias_dict, если он существует
        alias = alias_dict.get(username, username)

        # Проверяем, существует ли пользователь с таким alias
        try:
            user = get_user_model().objects.get(alias=alias)  # ищем по alias
            # Если пользователь существует, заменяем @username на ссылку
            return f'<a href="/channel/{alias}" class="mention-link">@{username}</a>'
        except get_user_model().DoesNotExist:
            # Если пользователя нет в базе по alias, возвращаем обычный текст @username
            return f'@{username}'

    return re.sub(r'@(\w+)', replace_with_link, value)

@register.simple_tag
def get_comment_vote(comment, user):
    try:
        vote = CommentsVoteModel.objects.get(user=user, content=comment)
        return vote.vote_type
    except:
        return None

@register.simple_tag
def get_user_vote(content, user, type):
    if type == 'video':
        try:
            vote = VoteModel.objects.get(user=user, content=content)
            return vote.vote_type
        except:
            return None
    elif type == 'post':
        try:
            vote = PostsVoteModel.objects.get(user=user, content=content)
            return vote.vote_type
        except:
            return None

@register.filter
def count_videos(pl):
    return VideoPlayListModel.objects.filter(playlist=pl).count()

@register.filter
def count_views(pl):
    pl_videos = VideoPlayListModel.objects.filter(playlist=pl)
    videos = [vp.video for vp in pl_videos]
    views = sum([get_views(video) for video in videos])
    if views == 1:
        word = 'просмотр'
    elif 1 < views < 5:
        word = 'просмотра'
    else:
        word = 'просмотров'

    return f'{views} {word}'

@register.simple_tag
def is_subscribed(author, user):
    return SubscribeModel.objects.filter(author=author, subscriber=user).exists()