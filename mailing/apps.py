from time import sleep

from django.apps import AppConfig


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'

    #def ready(self):
        #from jobs import updater
        #sleep(2)
        #updater.start()

    def ready(self):
        from django.core.management import call_command
        call_command('start_scheduler')