from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from users.views import RegisterView, ProfileView, EmailVerificationView, PasswordRecoveryView

app_name = 'user'

urlpatterns = [
    path('', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('password_recovery/', PasswordRecoveryView.as_view(), name='password_recovery'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('verify/<str:email>/<uuid:code>/', EmailVerificationView.as_view(), name='email_verification'),
]
