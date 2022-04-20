import requests

from datetime import datetime
from bs4 import BeautifulSoup


class WebScraping:
    def __init__(self):
        pass

    def scrap_f1_calendar(self):
        results = []
        current_year = datetime.now().year
        default_url  = f"https://www.espn.com/f1/schedule/_/year/{current_year}"

        html_page = requests.get(default_url)
        beautiful_soup = BeautifulSoup(html_page.content, "html.parser")

        table_result = beautiful_soup.find("table", attrs={"class": "Table"})
        table_body_result = table_result.find("tbody")
        table_body_result_rows = table_body_result.find_all("tr")

        for row in table_body_result_rows:
            cols = row.find_all("td")
            cols = [element.text.strip() for element in cols]
            results.append([element for element in cols if element])

        return results

    def scrap_f1_result(self):
        pass 