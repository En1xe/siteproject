import re

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django import forms
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Обновление виджетов и добавление стилей
        self.fields['username'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Введите пароль'
        })

        # Настройка меток для полей
        self.fields['username'].label = 'Имя пользователя'  # Установка метки для поля имени пользователя
        self.fields['password'].label = 'Пароль'           # Установка метки для поля пароля


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()  # Убедитесь, что используется пользовательская модель, если она есть
        fields = ('username', 'password1', 'password2', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем стили для полей формы
        self.fields['username'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Подтвердите пароль'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'login-input',
            'placeholder': 'Введите почту'
        })
        self.fields['username'].label = 'Имя пользователя'  # Установка метки для поля имени пользователя
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'  # Установка метки для поля имени пользователя
        self.fields['email'].label = 'Адрес почты'


class ProfileDataForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email']
        labels = {
            'username': 'Имя пользователя',
            'password': 'Пароль',
            'email': 'Адрес почты'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'profile-input'}),
            'username': forms.TextInput(attrs={'class': 'profile-input'}),
            'password': forms.TextInput(attrs={'class': 'profile-input'}),
        }


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'users/custom-file-input.html'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'class': 'custom-file-input'})
        super().__init__(*args, **kwargs)


class ProfileDesignForm(forms.ModelForm):
    alias = forms.CharField(max_length=17, label='Псевдоним', widget=forms.TextInput(attrs={'class': 'profile-input'}))

    class Meta:
        model = get_user_model()
        fields = ['banner', 'user_icon', 'alias', 'channel_description']  # Добавьте сюда ваши скрытые поля
        labels = {
            'banner': 'Баннер',
            'user_icon': 'Фото профиля',
            'channel_description': 'Описание канала'
        }
        widgets = {
            'banner': CustomClearableFileInput(attrs={'class': 'custom-file-input'}),
            'user_icon': CustomClearableFileInput(attrs={'class': 'custom-file-input'}),
            'channel_description': forms.Textarea(attrs={'class': 'profile-text-input',
                                                         'placeholder': 'Расскажите аудитории о своем канале.'}),
        }

    def clean_alias(self):
        alias = self.cleaned_data['alias']
        if (re.search(r'@[^A-Za-z0-9-_].', alias) and
                get_user_model().objects.filter(alias=alias).exists()):
            raise ValidationError("Псевдоним должен состоять из латинский букв, цифр, символов дефис или нижнее подчеркивание.")
        return alias


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Адрес почты', widget=forms.TextInput(attrs={'class': 'login-input'}))


class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label='Код безопасности', widget=forms.TextInput(attrs={
            'type': 'number',           # HTML-тип number
            'class': 'login-input',     # CSS-класс для стиля
            'placeholder': 'Введите код',
            'pattern': '[0-9]*',         # Ограничение на ввод только чисел
        }))

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError("Поле должно содержать только цифры.")
        return code


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "Новый пароль"
        self.fields['new_password2'].label = "Подтверждение пароля"
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={
            'class': 'login-input',
            'placeholder': 'Введите новый пароль',
        })
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={
            'class': 'login-input',
            'placeholder': 'Подтвердите новый пароль',
        })

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return password2

