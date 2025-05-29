# main/management/commands/uploadstatic.py

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders
from main.storages import StaticStorage

class Command(BaseCommand):
    help = "Upload all static files to S3 using your StaticStorage backend"

    def handle(self, *args, **options):
        storage = StaticStorage()
        total = 0

        for finder in finders.get_finders():
            for path, finder_storage in finder.list([]):
                total += 1
                self.stdout.write(f"[{total}] Uploading: {path}")
                with finder_storage.open(path) as f:
                    storage.save(path, f)

        self.stdout.write(self.style.SUCCESS(
            f"Done! Uploaded {total} static file(s) to S3."
        ))
