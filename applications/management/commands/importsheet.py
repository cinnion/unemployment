from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from applications.models import JobApplication
from googleapiclient.discovery import build


class Command(BaseCommand):
    help = 'Imports from the google spreadsheet'

    def handle(self, *args, **options):
        service = build(
            'sheets',
            'v4',
            developerKey=settings.GOOGLE_API_KEY)

        rangeName = "Clean!A2:G"
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=settings.GOOGLE_SPREADSHEET_ID,
                                    range=rangeName).execute()

        values = result.get("values", [])

        if not values:
            CommandError("No data found.")

        for row in values:
            dateParts = row[0].split('/')
            if (len(dateParts) == 2):
                year = 2023
                month, day = dateParts
            else:
                year, month, day = dateParts

            sqlDate= "{}-{}-{}".format(year, month, day)

            app = JobApplication()
            app.when = sqlDate
            if row[1] == '1' or row[1]=='':
                app.active = True
            else:
                app.active = False
            app.notes = row[2]
            app.company = row[3]
            if len(row) > 4:
                app.title = row[4]
            if len(row) > 5:
                if row[5][:4] == 'http':
                    app.posting = row[5]
                else:
                    app.notes = row[5]
            if len(row) > 6:
                app.confirm = row[6]

            app.save()

            self.stdout.write(
                self.style.SUCCESS('Successfully read for "{}" on {}'.format(row[3], sqlDate))
            )
