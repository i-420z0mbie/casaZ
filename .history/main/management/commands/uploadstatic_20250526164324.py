from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders
from main.storages import StaticStorage


class Command(BaseCommand):
    help = "Upload all static files to S3 using your StaticStorage backend"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List the static files that would be uploaded without actually uploading them.'
        )

    def handle(self, *args, **options):
        storage = StaticStorage()
        total = 0
        dry_run = options['dry_run']

        for finder in finders.get_finders():
            for path, finder_storage in finder.list([]):
                total += 1
                self.stdout.write(f"[{total}] {'Would upload' if dry_run else 'Uploading'}: {path}")
                if not dry_run:
                    with finder_storage.open(path) as f:
                        storage.save(path, f)

        self.stdout.write(self.style.SUCCESS(
            f"{'Dry run complete!' if dry_run else 'Done!'} {total} static file(s) {'listed' if dry_run else 'uploaded'}."
        ))
