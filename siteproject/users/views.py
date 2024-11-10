from datetime import timedelta

from django.contrib.auth import logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView

from siteproject import settings
from users.forms import LoginForm, RegistrationForm, ProfileDataForm, ProfileDesignForm, PasswordResetRequestForm, \
    CodeVerificationForm, CustomSetPasswordForm
from users.models import PasswordResetCode


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



class ProfileDesign(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_design.html'
    model = get_user_model()
    form_class = ProfileDesignForm

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        banner_clear_value = self.request.POST.get('banner_clear')
        user_icon_clear_value = self.request.POST.get('user_icon_clear')

        if banner_clear_value == 'true':
            print("Удаление баннера...")
            if form.instance.banner:
                form.instance.banner.delete(save=False)
                form.instance.banner = 'default_banner/default_banner.png'
                print("Баннер удален.")
            else:
                print("Баннер не установлен.")

        if user_icon_clear_value == 'true':
            print("Удаление иконки...")
            if form.instance.user_icon:
                form.instance.user_icon.delete(save=False)
                form.instance.user_icon = 'default_icon/user_icon.png'
                print("Иконка пользователя удалена.")
            else:
                print("Иконка пользователя не установлена.")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['is_default_banner'] = user.is_default_banner()
        context['is_default_user_icon'] = user.is_default_user_icon()
        return context


class RequestPasswordResetView(View):
    template_name = 'users/request_password_reset.html'
    form_class = PasswordResetRequestForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = get_user_model().objects.get(email=email)

                # Генерация нового кода и установка времени истечения
                code = PasswordResetCode.generate_code()
                expiration_time = timezone.now() + timedelta(minutes=10)

                # Удаление существующего кода для пользователя, если есть
                PasswordResetCode.objects.filter(user=user).delete()

                # Сохранение нового кода в базе данных
                PasswordResetCode.objects.create(user=user, code=code, expiration_time=expiration_time)

                # Отправка кода на почту
                send_mail(
                    'Ваш код для восстановления пароля',
                    f'Ваш код для восстановления пароля: {code}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return redirect('users:verify_code')  # Переход на страницу ввода кода
            except get_user_model().DoesNotExist:
                form.add_error('email', 'Пользователь с таким адресом не найден')
        return render(request, self.template_name, {'form': form})


class VerifyCodeView(View):
    template_name = 'users/verify_code.html'
    form_class = CodeVerificationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                reset_code = PasswordResetCode.objects.get(code=code)

                # Проверка срока действия кода
                if reset_code.is_valid():
                    # Код верный и не истек, перенаправляем пользователя на форму сброса пароля
                    return redirect('users:password_reset_form', user_id=reset_code.user.id)
                else:
                    form.add_error('code', 'Код истек, запросите новый.')

            except PasswordResetCode.DoesNotExist:
                form.add_error('code', 'Неверный код.')

        # Если код неверен или истек, отображаем форму с ошибкой
        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    template_name = 'users/reset_password.html'
    form_class = CustomSetPasswordForm

    def get(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        form = self.form_class(user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        form = self.form_class(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')  # перенаправление на страницу входа после успешного сброса
        return render(request, self.template_name, {'form': form})


