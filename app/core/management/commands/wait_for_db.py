import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command for pause execution until the database is available"""

    def handle(self, *args, **options):
        print("Waiting for database")
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections['default']
            except OperationalError:
                print(self.style.ERROR("Database not available"))
                time.sleep(1)
        print(self.style.SUCCESS("Database available"))
