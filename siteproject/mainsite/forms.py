from django import forms

from mainsite.models import VideoModel, CommentModel, PlayListModel, PostsModel, Feedback

class CustomVideoFileInput(forms.ClearableFileInput):
    template_name = 'mainsite/custom_video_input.html'


class CustomImageFileInput(forms.ClearableFileInput):
    template_name = 'mainsite/custom_image_input.html'


class DownloadForm(forms.ModelForm):
    class Meta:
        model = VideoModel
        fields = ['title', 'description', 'file', 'picture', 'access']
        labels = {
            'file': 'Видеофайл',
            'title': 'Название',
            'description': 'Описание',
            'picture': 'Картинка',
            'access': 'Доступ'
        }
        widgets = {
            'file': CustomVideoFileInput(attrs={'class': 'custom-file-input'}),
            'title': forms.TextInput(attrs={'class': 'video-input', 'placeholder': 'Название видео'}),
            'description': forms.Textarea(attrs={'class': 'video-input-area', 'placeholder': 'Расскажите, о чем ваше видео'}),
            'picture': CustomImageFileInput(attrs={'class': 'custom-file-input'}),
            'access': forms.Select(attrs={'class': 'custom-access-select'})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['text']
        labels = {
            'text': ''
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'comment-input-field',
                                          'id': "auto-resize",
                                          'placeholder': 'Введите комментарий',
                                          'name': 'comment'
            })
        }


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = PlayListModel
        fields = ['title', 'access']
        labels = {
            'title': 'Название',
            'access': 'Доступ'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'playlist-text-input'}),
            'access': forms.Select(attrs={'class': 'custom-access-select'})
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = PostsModel
        fields = ['text', 'image']
        labels = {
            'text': 'Текст',
            'image': 'Картинка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'post-input-area', 'placeholder': 'Расскажите, о чем ваш пост'}),
            'image': CustomImageFileInput(attrs={'class': 'custom-file-input'})
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        labels = {
            'comment': 'Отзыв'
        }
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'feedback-text-input',
                                             'placeholder': 'Расскажите, почему решили отправить отзыв'}),
        }