from django.core.management.base import BaseCommand, CommandError
from matialvarezs_node_configurations import initialize_table_configurations
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass  # parser.add_argument('-f', '--foo')

    def handle(self, *args, **options):
        # foo = options["foo"]
        initialize_table_configurations.initialize()
        #pass