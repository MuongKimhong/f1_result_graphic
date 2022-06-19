from django.core.management.base import BaseCommand, CommandError
from web_scraping.script import WebScraping, Graphic


class Command(BaseCommand):
    help = "Test on web scraping function for f1 calendar"

    def handle(self, *args, **options):
        web_scraping = WebScraping()
        # 600014127 race id (bahrain) from ESPN Site
        f1_result = web_scraping.scrap_f1_result(600014127)

        g = Graphic()
        g.generate_graphic(f1_result)