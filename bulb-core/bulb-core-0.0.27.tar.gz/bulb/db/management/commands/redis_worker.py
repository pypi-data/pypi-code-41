from django.core.management.base import BaseCommand
from bulb.db import redis_worker


class Command(BaseCommand):
    args = ''
    help = """
            Start the redis worker
            """

    def handle(self, *args, **options):
        redis_worker.work()