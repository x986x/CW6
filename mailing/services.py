import logging
from datetime import datetime, timedelta
import pytz
from django.conf import settings
from django.core.mail import send_mail
from mailing.models import Mailing, Log

logger = logging.getLogger(__name__)


def send_mailings():
    tz = pytz.timezone('Europe/Moscow')
    current_datetime = datetime.now(tz)
    logger.info("Running send_mailings at %s", current_datetime)

    for mailing in Mailing.objects.filter(status='started'):
        logger.info("Processing mailing: %s", mailing)

        is_mailing = False
        emails = [client.email for client in mailing.recipients.all()]
        hour_start = mailing.start_time.hour
        minute_start = mailing.start_time.minute
        attempt_status = 'success'
        server_response = 'Email sent successfully'
        messages = mailing.message_set.all()

        if mailing.frequency == 'daily' and current_datetime >= mailing.start_time \
                and current_datetime.hour == hour_start and current_datetime.minute == minute_start:
            mailing.start_time = mailing.start_time + timedelta(days=1)
            is_mailing = True

        elif mailing.frequency == 'weekly' and current_datetime >= mailing.start_time \
                and current_datetime.weekday() == mailing.start_time.weekday() \
                and current_datetime.hour == hour_start and current_datetime.minute == minute_start:
            mailing.start_time = mailing.start_time + timedelta(weeks=1)
            is_mailing = True

        elif mailing.frequency == 'monthly' and current_datetime >= mailing.start_time \
                and current_datetime.day == mailing.start_time.day \
                and current_datetime.hour == hour_start and current_datetime.minute == minute_start:
            mailing.start_time = mailing.start_time + timedelta(days=30)
            is_mailing = True

        if is_mailing:
            mailing.status = 'started'
            mailing.save()
            logger.info("Sending emails for mailing: %s", mailing)
            for message in messages:
                try:
                    send_mail(
                        subject=message.subject,
                        message=message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=emails
                    )
                    logger.info("Email sent successfully to: %s", emails)
                except Exception as e:
                    attempt_status = 'error'
                    server_response = str(e)
                    logger.error("Failed to send email: %s", server_response)
                finally:
                    Log.objects.create(
                        message=message,
                        status=attempt_status,
                        response=server_response
                    )

            mailing.status = 'completed'
            mailing.save()
