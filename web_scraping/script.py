import requests

from datetime import datetime
from bs4 import BeautifulSoup


class WebScraping:
    def __init__(self):
        pass

    def scrap_f1_calendar(self):
        results = []
        formatted_results = []
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

        for result in results:
            date = result[0]
            object = {
                'season': str(current_year),
                'start_date': f"{date.split(' ')[0]} {date.split(' ')[1]}",
                'end_date': f"{date.split(' ')[0]} {date.split(' ')[3]}",
                'track': result[1]
            }
            formatted_results.append(object)

        return formatted_results

    def scrap_f1_result(self):
        pass 