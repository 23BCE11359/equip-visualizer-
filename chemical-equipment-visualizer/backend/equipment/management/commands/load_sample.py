from django.core.management.base import BaseCommand
from django.conf import settings
import os
import pandas as pd
from equipment.models import Dataset, Equipment


class Command(BaseCommand):
    help = 'Load sample_equipment_data.csv into the database (creates a Dataset)'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to CSV file (default: backend/sample_equipment_data.csv)')

    def handle(self, *args, **options):
        fpath = options.get('file')
        if not fpath:
            fpath = os.path.join(settings.BASE_DIR, 'sample_equipment_data.csv')

        if not os.path.exists(fpath):
            self.stdout.write(self.style.ERROR(f'File not found: {fpath}'))
            return

        df = pd.read_csv(fpath)
        dataset = Dataset.objects.create(name=os.path.basename(fpath))
        created = 0
        for _, row in df.iterrows():
            try:
                Equipment.objects.create(
                    dataset=dataset,
                    name=row.get('Equipment Name') or row.get('name') or '',
                    type=row.get('Type') or row.get('type') or '',
                    flowrate=float(row.get('Flowrate') or 0),
                    pressure=float(row.get('Pressure') or 0),
                    temperature=float(row.get('Temperature') or 0),
                    material=row.get('Material') or ''
                )
                created += 1
            except Exception as e:
                continue

        self.stdout.write(self.style.SUCCESS(f'Loaded dataset "{dataset.name}" with {created} equipment rows'))