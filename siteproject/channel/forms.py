from django import forms

from mainsite.models import VideoModel, PostsModel


class CustomFileInput(forms.ClearableFileInput):
    template_name = 'channel/custom-edit-content-input.html'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'class': 'custom-file-input'})
        super().__init__(*args, **kwargs)


class EditContentForm(forms.ModelForm):
    class Meta:
        model = VideoModel
        fields = ['title', 'description', 'picture', 'access']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'picture': 'Картинка видео',
            'access': 'Доступ'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'edit-content-text-input',
                                             'placeholder': 'Укажите название видео'}),
            'description': forms.Textarea(attrs={'class': 'edit-content-text-input',
                                             'placeholder': 'Расскажите, о чем ваше видео'}),
            'picture': CustomFileInput(attrs={'class': 'custom-file-input'}),
            'access': forms.Select(attrs={
                'class': 'custom-access-select',
            }),
        }

class EditPostForm(forms.ModelForm):
    class Meta:
        model = PostsModel
        fields = ['text', 'image']
        labels = {
            'text': 'Текст',
            'image': 'Картинка'
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'edit-content-text-input',
                                                 'placeholder': 'Текст вашего поста'}),
            'image': CustomFileInput(attrs={'class': 'custom-file-input'}),
        }
