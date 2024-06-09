from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    def __str__(self):
        return self.full_name


class Mailing(models.Model):
    start_time = models.DateTimeField()
    frequency_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    frequency = models.CharField(max_length=10, choices=frequency_choices)
    status_choices = [
        ('created', 'Created'),
        ('started', 'Started'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices)
    recipients = models.ManyToManyField('Client')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)
    end_time = models.DateTimeField(**NULLABLE)

    class Meta:
        permissions = [
            ("can_view_mailings", "Can view mailings"),
            ("can_disable_mailings", "Can disable mailings"),
        ]

    def save(self, *args, **kwargs):
        if not self.end_time:
            if self.frequency == 'daily':
                self.end_time = self.start_time + timedelta(days=1)
            elif self.frequency == 'weekly':
                self.end_time = self.start_time + timedelta(weeks=1)
            elif self.frequency == 'monthly':
                self.end_time = self.start_time + timedelta(days=30)
        super().save(*args, **kwargs)


class Message(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE)


class Log(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    response = models.TextField(blank=True)