import json
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from axiohm.settings import BASE_DIR
from users.models import User


class Command(BaseCommand):
    help = 'Удалить всех пользователей и группы и создать суперюзера и группу менджер'

    def handle(self, *args, **kwargs):
        Group.objects.all().delete()
        User.objects.all().delete()
        user = User.objects.create(
            email=settings.EMAIL_HOST_USER,
            first_name='Admin',
            last_name='Axiohm',
            is_staff=True,
            is_superuser=True
        )
        user.set_password(os.getenv('ADMIN_PASSWORD'))
        user.save()
        with open(BASE_DIR / 'users/fixtures/groups_fixture.json', 'r', encoding='cp1251') as file:
            group_data = json.load(file)
            for item in group_data:
                group = Group.objects.create(
                    pk=item['pk'],
                    name=item['fields']['name'],
                )
                group.permissions.set(item['fields']['permissions'])
