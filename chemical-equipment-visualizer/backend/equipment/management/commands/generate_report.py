from django.core.management.base import BaseCommand
from equipment.models import Dataset
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate a PDF report for a dataset and save it to a file. Usage: manage.py generate_report --dataset <id> --out <path>'

    def add_arguments(self, parser):
        parser.add_argument('--dataset', type=int, required=True, help='Dataset id')
        parser.add_argument('--out', type=str, required=False, help='Output path (default: backend/docs/dataset_<id>.pdf)')

    def handle(self, *args, **options):
        ds_id = options.get('dataset')
        out = options.get('out')
        try:
            ds = Dataset.objects.get(pk=ds_id)
        except Dataset.DoesNotExist:
            self.stdout.write(self.style.ERROR('Dataset not found'))
            return

        if not out:
            docs_dir = os.path.join(settings.BASE_DIR, 'docs')
            os.makedirs(docs_dir, exist_ok=True)
            out = os.path.join(docs_dir, f'dataset_{ds_id}.pdf')
        else:
            out_dir = os.path.dirname(out)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

        # Use the existing view function logic by calling the view and writing binary content
        from equipment.views import dataset_report_pdf
        from rest_framework.test import APIRequestFactory
        from rest_framework.authtoken.models import Token
        factory = APIRequestFactory()
        user = None
        # Use the first superuser if exists, else create a temp user
        from django.contrib.auth.models import User
        users = User.objects.filter(is_superuser=True)
        if users.exists():
            user = users.first()
        else:
            user, _ = User.objects.get_or_create(username='report-temp')
        token, _ = Token.objects.get_or_create(user=user)

        req = factory.get(f'/api/datasets/{ds_id}/report/pdf/')
        req.META['HTTP_AUTHORIZATION'] = 'Token ' + token.key

        resp = dataset_report_pdf(req, ds_id)
        if resp.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to generate report: status {resp.status_code}'))
            return

        with open(out, 'wb') as fh:
            fh.write(resp.content)

        self.stdout.write(self.style.SUCCESS(f'Report written to {out}'))