from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Почта')
    avatar = models.ImageField(upload_to='users/', null=True, blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=35, verbose_name='Телефон')
    country = models.CharField(max_length=35, verbose_name='Страна')
    is_verified_email = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'EmailVerification object for {self.user.email}'

    def send_verification_email(self):
        link = reverse('user:email_verification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = settings.DOMAIN_NAME + link
        subject = 'Подтверждение учетной записи'
        message = f'Для подтверждения перейдите по ссылке: {verification_link}'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return now() >= self.expiration