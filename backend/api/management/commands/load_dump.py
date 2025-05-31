from django.core.management.base import BaseCommand
from django.db import connection
import os


class Command(BaseCommand):
    """Load dump.sql into the database using Django."""

    def handle(self, *args, **kwargs):
        dump_file_path = os.path.join(
            os.path.dirname(__file__), '../../../dump.sql'
        )

        if not os.path.exists(dump_file_path):
            self.stderr.write(
                self.style.ERROR(
                    f'dump.sql file not found at {dump_file_path}'
                )
            )
            return

        try:
            self.stdout.write(
                'Loading dump.sql into the database using Django...'
            )
            with open(dump_file_path, 'r') as dump_file:
                sql_commands = dump_file.read()

            with connection.cursor() as cursor:
                cursor.execute(sql_commands)

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully loaded dump.sql into the database using '
                    'Django.'
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error loading dump.sql: {e}')
            )
