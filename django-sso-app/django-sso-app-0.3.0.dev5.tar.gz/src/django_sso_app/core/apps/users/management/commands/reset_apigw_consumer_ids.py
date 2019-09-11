from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Sets apigw_consumer_id to None'

    def handle(self, *args, **options):
        users = User.objects.all()
        users_count = users.count()
        updated_users = 0
        for user in users:
            user.apigw_consumer_id = None
            user.save()

        self.stdout.write(self.style.SUCCESS('Updated {0}/{1} Users'.format(users_count, updated_users)))
