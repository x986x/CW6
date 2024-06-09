from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, UpdateView, TemplateView
from django.views.generic.edit import FormView

from users.forms import UserRgisterForm, UserProfileForm, PasswordRecoveryForm
from users.models import User, EmailVerification


class RegisterView(CreateView):
    model = User
    form_class = UserRgisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy("user:login")


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy("user:profile")

    def get_object(self, queryset=None):
        return self.request.user


class EmailVerificationView(TemplateView):
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('/'))


class PasswordRecoveryView(FormView):
    template_name = 'users/password_recovery.html'
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy('user:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)
        length = 12
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        password = get_random_string(length, alphabet)
        user.set_password(password)
        user.save()
        subject = 'Password Recovery'
        message = f'Your new password: {password}'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)