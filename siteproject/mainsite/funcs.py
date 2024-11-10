from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from mainsite.models import SubscribeModel, CommentModel, CommentsVoteModel

from django.http import JsonResponse
from django.contrib.auth import get_user_model

def handle_subscription_action(request):
    author_id = request.POST.get('author_id')
    action_type = request.POST.get('action_type')

    if not author_id:
        return JsonResponse({'error': 'author_id не был получен'}, status=400)

    try:
        # Получаем объект автора по ID
        author = get_user_model().objects.get(id=author_id)
    except get_user_model().DoesNotExist:
        return JsonResponse({'error': 'Автор не найден'}, status=404)

    # Проверка действия - подписка
    if action_type == 'subscribe':
        subscription, created = SubscribeModel.objects.get_or_create(
            subscriber=request.user,
            author=author
        )
        # Возвращаем ответ с информацией о подписке
        return JsonResponse({
            'is_subscribed': created,
            'author_username': author.username,
            'message': 'Вы успешно подписались!' if created else 'Вы уже подписаны на этого автора.'
        })

    # Проверка действия - отписка
    elif action_type == 'unsubscribe':
        try:
            subscription = SubscribeModel.objects.get(
                subscriber=request.user,
                author=author
            )
            subscription.delete()
            return JsonResponse({
                'is_unsubscribed': True,
                'author_username': author.username,
                'message': 'Вы отписались от автора.'
            })
        except SubscribeModel.DoesNotExist:
            return JsonResponse({'error': 'Подписка не найдена'}, status=404)

    # Если action_type не правильный
    return JsonResponse({'error': 'Invalid action'}, status=400)



def handle_vote(request, content, vote_type, model):
    existing_vote = model.objects.filter(user=request.user, content=content)

    if existing_vote.exists():
        existing_vote = existing_vote.first()
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        model.objects.create(user=request.user, vote_type=vote_type, content=content)

    likes_count = model.objects.filter(vote_type='like', content=content).count()
    dislikes_count = model.objects.filter(vote_type='dislike', content=content).count()

    return JsonResponse({'likes_count': likes_count, 'dislikes_count': dislikes_count})


def vote_on_comment(request, comment_id, vote_type):
    # Получаем объект комментария
    comment = get_object_or_404(CommentModel, id=comment_id)

    # Получаем или создаем голосование
    vote, created = CommentsVoteModel.objects.get_or_create(
        user=request.user,
        content=comment
    )

    # Если голос уже существует и его тип совпадает с новым, то удаляем голос
    if not created and vote.vote_type == vote_type:
        vote.delete()
        user_liked = False
        user_disliked = False
    else:
        # Если голос изменился, сохраняем новый
        vote.vote_type = vote_type
        vote.save()
        user_liked = (vote_type == 'like')
        user_disliked = (vote_type == 'dislike')

    # Подсчитываем количество лайков и дизлайков
    likes_count = CommentsVoteModel.objects.filter(vote_type='like', content=comment).count()
    dislikes_count = CommentsVoteModel.objects.filter(vote_type='dislike', content=comment).count()

    # Возвращаем результат в формате JSON
    return JsonResponse({
        'likes_count': likes_count,
        'dislikes_count': dislikes_count,
        'user_liked': user_liked,
        'user_disliked': user_disliked
    })