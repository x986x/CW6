from django import forms
from .models import Mailing, Message, Client


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'frequency', 'recipients', 'status']
        widgets = {
            'recipients': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MailingForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['recipients'].queryset = user.client_set.all()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment', 'is_active']

        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),  # Можно настроить виджет для текстового поля 'comment'
        }

