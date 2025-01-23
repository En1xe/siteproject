from django.urls import path
from .views import Login, Registration, Logout, ProfileData, ProfileDesign, VerifyChangeCodeView, SendSecurityCodeView, \
    ChangePasswordView, ChangeEmailView

app_name = "users"

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('registration/', Registration.as_view(), name='registration'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile_data/', ProfileData.as_view(), name='profile_data'),
    path('profile_design/', ProfileDesign.as_view(), name='profile_design'),
    path('verification', VerifyChangeCodeView.as_view(), name='verification'),
    path('send_code', SendSecurityCodeView.as_view(), name='send_code'),
    path('change_password', ChangePasswordView.as_view(), name='change_password'),
    path('change_email', ChangeEmailView.as_view(), name='change_email')
]