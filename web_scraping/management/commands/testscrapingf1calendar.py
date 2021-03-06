from django.core.management.base import BaseCommand, CommandError
from web_scraping.script import WebScraping


class Command(BaseCommand):
    help = "Test on web scraping function for f1 calendar"

    def handle(self, *args, **options):
        web_scraping = WebScraping()
        f1_calendar = web_scraping.scrap_f1_calendar()

        for data in f1_calendar:
            print(data)