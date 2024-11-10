from django.urls import path
from .views import Login, Registration, Logout, ProfileData, ProfileDesign, RequestPasswordResetView, VerifyCodeView, \
    ResetPasswordView

app_name = "users"

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('registration/', Registration.as_view(), name='registration'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile_data/', ProfileData.as_view(), name='profile_data'),
    path('profile_design/', ProfileDesign.as_view(), name='profile_design'),
    path('password-reset/', RequestPasswordResetView.as_view(), name='password_reset'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('password-reset/<int:user_id>/', ResetPasswordView.as_view(), name='password_reset_form'),
]