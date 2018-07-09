from django.core.management.base import BaseCommand, CommandError
from crawlers.models import Observatory


class Command(BaseCommand):
    help = 'Create Observatory database set'

    def _create_observatory(self):
        f = open('crawlers/management/data/observatory_seoul.csv', 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            tmp = line.split(',')
            obs = Observatory()
            obs.aws_code = tmp[1]
            obs.name = tmp[2]
            obs.aws_type_name = tmp[3]
            obs.lng = tmp[4]
            obs.lat = tmp[5]
            obs.address = tmp[6]
            obs.save()

    def handle(self, *args, **options):
        self._create_observatory()
