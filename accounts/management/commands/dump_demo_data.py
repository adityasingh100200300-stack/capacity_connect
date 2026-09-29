import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Exports all current accounts, profiles, courses, and announcements to fixtures/demo_data.json so they can be committed to Git."

    def handle(self, *args, **options):
        fixtures_dir = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)
        fixture_file = os.path.join(fixtures_dir, "demo_data.json")

        self.stdout.write(self.style.MIGRATE_HEADING("Exporting current data to fixtures/demo_data.json..."))

        with open(fixture_file, "w", encoding="utf-8") as f:
            call_command(
                "dumpdata",
                "accounts",
                "profiles",
                "courses",
                "announcements",
                natural_foreign=True,
                natural_primary=True,
                indent=2,
                stdout=f,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Successfully saved current data to: {fixture_file}"))
        self.stdout.write(
            "You can now run:\n"
            "  git add fixtures/demo_data.json\n"
            "  git commit -m \"Update demo accounts and courses\"\n"
            "  git push\n"
        )
