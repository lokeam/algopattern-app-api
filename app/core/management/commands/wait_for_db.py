"""
Django cmd to wait for db availability
"""
import time

from psycopg2 import OperationalError as Pyscopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Waiting for db...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Pyscopg2OpError, OperationalError):
                self.stdout.write('Db unavailable, waiting a second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Huzzah! Dbs available'))
