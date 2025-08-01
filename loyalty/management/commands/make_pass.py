# yourapp/management/commands/make_pass.py
from django.core.management.base import BaseCommand
from loyalty.utility import create_pass

class Command(BaseCommand):
    help = "Generate a .pkpass for a given patient appointment"

    def add_arguments(self, parser):
        parser.add_argument("--patient-id", type=int, required=True)
        parser.add_argument("--appointment-id", type=int, required=True)
        parser.add_argument("--output", type=str, default="pass.pkpass")

    def handle(self, *args, **options):
        pkpass = create_pass()
        with open(options["output"], "wb") as f:
            f.write(pkpass)
        self.stdout.write(self.style.SUCCESS(f"Written {options['output']}"))
