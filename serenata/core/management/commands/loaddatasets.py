import csv
import lzma
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand

from serenata.core.models import Document


class Command(BaseCommand):
    help = 'Load Serenata de Amor datasets into the database'
    created = 0
    updated = 0

    def parse(self):
        """Load datasets and return a dict similar to model Document"""
        suffixes = ('current-year', 'last-year', 'previous-years')
        for url in map(self.get_url, suffixes):
            print("Loading " + url)
            with NamedTemporaryFile() as tmp:
                urlretrieve(url, filename=tmp.name)
                with lzma.open(tmp.name, mode='rt') as file_handler:
                    for row in csv.DictReader(file_handler):
                        if not self.has_reached_the_limit():
                            yield row
                        else:
                            break
            if self.has_reached_the_limit():
                break


    def handle(self, *args, **options):
        """Create or update records (if they match `document_id`)"""
        for document in map(self.serialize, self.parse()):
            obj, created = Document.objects.update_or_create(
                document_id=document['document_id'],
                defaults=document
            )
            if created:
                self.created += 1
            else:
                self.updated += 1
            msg = "{:,} records created / {:,} records updated                "
            print(msg.format(self.created, self.updated), end="\r")

    def serialize(self, document):
        """Read the dict generated by DictReader and fix content types"""
        integers = (
            'document_id',
            'congressperson_id',
            'congressperson_document',
            'term',
            'term_id',
            'subquota_number',
            'subquota_group_id',
            'document_type',
            'month',
            'year',
            'installment',
            'batch_number',
            'reimbursement_number',
            'applicant_id'
        )
        for key in integers:
            document[key] = self.to_number(document[key], int)

        floats = (
            'document_value',
            'remark_value',
            'net_value',
            'reimbursement_value'
        )
        for key in floats:
            document[key] = self.to_number(document[key], float)

        if document['issue_date'] == '':
            document['issue_date'] = None

        return document

    def has_reached_the_limit(self):
        limit = settings.DATABASE_LIMIT
        total = self.created + self.updated
        if limit and total >= limit:
            return True
        return False

    @staticmethod
    def get_url(suffix):
        file_name = '{date}-{suffix}.xz'.format(
            date=settings.AMAZON_S3_DATASET_DATE,
            suffix=suffix
        )
        url = 'https://{region}.amazonaws.com/{bucket}/{file_name}'.format(
            region=settings.AMAZON_S3_REGION,
            bucket=settings.AMAZON_S3_BUCKET,
            file_name=file_name
        )
        return url

    @staticmethod
    def to_number(value, type_of_number):
        return 0 if value in ('NaN', '') else type_of_number(value)
