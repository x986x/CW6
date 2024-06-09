from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from mailing.services import send_mailings
import logging

logger = logging.getLogger(__name__)

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Starts the APScheduler."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        try:
            scheduler.add_job(
                send_mailings,
                trigger=CronTrigger(minute="*/1"),
                id="send_mailings",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'send_mailings'.")

            scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'delete_old_job_executions'.")

            scheduler.start()
            logger.info("Scheduler started successfully.")

        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully.")
