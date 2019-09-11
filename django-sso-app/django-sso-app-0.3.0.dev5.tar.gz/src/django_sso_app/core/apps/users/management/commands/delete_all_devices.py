from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes all devices (and jwts)'

    def handle(self, *args, **options):
        users = User.objects.all()
        users_count = users.count()
        updated_users = 0
        for user in users:
            
            devices_count = user.devices.count()
            deleted_devices_count = user.remove_all_user_devices()

            self.stdout.write(self.style.SUCCESS('Deleted {0}/{1} user devices for "{2}"'.format(devices_count, deleted_devices_count, user)))
            
            updated_users += 1

        self.stdout.write(self.style.SUCCESS('Updated {0}/{1} Users'.format(users_count, updated_users)))
