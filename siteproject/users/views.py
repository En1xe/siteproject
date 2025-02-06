from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, UpdateView

from siteproject import settings
from users.forms import LoginForm, RegistrationForm, ProfileDataForm, ProfileDesignForm, CodeVerificationForm, \
    CustomSetPasswordForm, ChangeEmailForm
from users.models import SecurityCode


class Login(LoginView):
    template_name = 'users/login_page.html'
    form_class = LoginForm

    def get_form(self, form_class=None):
        # Передаем request в форму
        form = super().get_form(form_class)
        form.request = self.request  # Передаем request в форму
        return form

class Registration(CreateView):
    template_name = 'users/register_page.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')


class Logout(LogoutView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ProfileData(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_data.html'
    model = get_user_model()
    form_class = ProfileDataForm

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type', '')
        user_alias = request.POST.get('user_alias', '')

        if action_type == 'delete-account':
            if user_alias == self.request.user.alias:
                user = self.request.user
                user.delete()
                logout(request)
                return redirect('/')
            return JsonResponse({'message': 'Недостаточно прав для удаления аккаунта'}, status=403)
        return super().post(request, *args, **kwargs)


class ProfileDesign(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_design.html'
    model = get_user_model()
    form_class = ProfileDesignForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        banner_clear_value = self.request.POST.get('banner_clear')
        user_icon_clear_value = self.request.POST.get('user_icon_clear')

        if banner_clear_value == 'true':
                form.instance.banner.delete(save=False)
                form.instance.banner = 'default_banner/default_banner.png'

        if user_icon_clear_value == 'true':
                form.instance.user_icon.delete(save=False)
                form.instance.user_icon = 'default_icon/user_icon.png'

        return super().form_valid(form)


class SendSecurityCodeView(View):
    def post(self, request):
        action = request.POST.get('action')

        if not action or action not in ['change_password', 'change_email']:
            messages.error(request, 'Некорректное действие.')
            return

        user = request.user

        # Генерация кода
        code = SecurityCode.generate_code()

        # Удаляем предыдущий код
        SecurityCode.objects.filter(user=user).delete()

        # Устанавливаем время истечения (например, через 10 минут)
        expiration_time = now() + timedelta(minutes=10)

        # Сохраняем новый код
        SecurityCode.objects.create(user=user, code=code, expiration_time=expiration_time)

        # Отправка кода на почту
        send_mail(
            'Код безопасности',
            f'Ваш код безопасности: {code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(request, 'Код безопасности отправлен на вашу почту.')
        return redirect(f"{reverse('users:verification')}?action={action}")


class VerifyChangeCodeView(View):
    template_name = 'users/verification.html'
    form_class = CodeVerificationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            user = request.user

            try:
                reset_code = SecurityCode.objects.get(code=code)

                if reset_code.is_valid():  # Проверка, действителен ли код
                    action = request.GET.get('action')
                    if action == 'change_password':
                        return redirect('users:change_password')
                    elif action == 'change_email':
                        return redirect('users:change_email')
                    elif action == 'verify_email':
                        new_email = reset_code.new_email
                        user.email = new_email
                        user.save()
                        return redirect('users:profile_data')
                    else:
                        messages.error(request, 'Неизвестное действие.')
                        return redirect('users:verify_change_code')
                else:
                    messages.error(request, 'Код истек. Запросите новый.')
            except SecurityCode.DoesNotExist:
                messages.error(request, 'Неверный код.')

        # Если форма не валидна или код не найден
        return render(request, self.template_name, {'form': form})


class ChangePasswordView(View):
    template_name = 'users/change_password_or_email.html'

    def get(self, request):
        # Создаем форму для смены пароля, передаем user через kwargs
        form = CustomSetPasswordForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Создаем форму для смены пароля, передаем user через kwargs
        form = CustomSetPasswordForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                # Сохраняем новый пароль
                form.save()

                # Обновляем сессию, чтобы не требовалась повторная аутентификация
                update_session_auth_hash(request, form.user)

                # Выводим сообщение об успешной смене пароля
                messages.success(request, 'Пароль успешно изменен!')

                # Перенаправляем на страницу профиля пользователя
                return redirect('users:profile_data')

            except Exception as e:
                # Обрабатываем ошибки при сохранении пароля
                messages.error(request, f'Произошла ошибка: {str(e)}')
                return render(request, self.template_name, {'form': form})

        # В случае ошибок валидации
        messages.error(request, 'Используйте правильный формат пароля или убедитесь в правильности ввода.')
        # Возвращаем форму с ошибками на страницу
        return render(request, self.template_name, {'form': form})


class ChangeEmailView(View):
    template_name = 'users/change_password_or_email.html'
    form_class = ChangeEmailForm

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            user = request.user

            # Генерация кода безопасности
            code = SecurityCode.generate_code()
            expiration_time = timezone.now() + timedelta(minutes=10)

            # Удаляем старые коды
            SecurityCode.objects.filter(user=user).delete()
            # Сохраняем новый код безопасности
            SecurityCode.objects.create(user=user, code=code, expiration_time=expiration_time, new_email=new_email)

            # Отправка кода на новый email
            send_mail(
                'Код безопасности для смены почты',
                f'Ваш код безопасности для смены почты: {code}',
                settings.EMAIL_HOST_USER,
                [new_email],
                fail_silently=False,
            )

            # Уведомление пользователя о запросе
            messages.success(request, f'Код безопасности для смены почты отправлен на {new_email}')
            return redirect(f"{reverse('users:verification')}?action=verify_email")

        return render(request, self.template_name, {'form': form})