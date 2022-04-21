import requests

from datetime import datetime
from bs4 import BeautifulSoup


class WebScraping:
    def __init__(self):
        "ESPN f1 2022 season id start from 600014127 (Bahrain) - 600014149 (Abu Dahbi)"
        self.espn_site_season_race_id = 600014127

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

        for (index, result) in enumerate(results):
            date = result[0]
            object = {
                'season': str(current_year),
                'start_date': f"{date.split(' ')[0]} {date.split(' ')[1]}",
                'end_date': f"{date.split(' ')[0]} {date.split(' ')[3]}",
                'track': result[1],
                'race_id': self.espn_site_season_race_id + index
            }
            formatted_results.append(object)

        return formatted_results

    def get_total_deciseconds(self, deciseconds, seconds=None, minutes=None):
        total_deciseconds = 0

        if (seconds is None) and (minutes is None):
            return deciseconds

        if (seconds is not None) and (minutes is None):
            total_deciseconds = deciseconds + (seconds * 10)
        elif (seconds is None) and (minutes is not None):
            total_deciseconds = deciseconds + (minutes * 600)
        else:
            total_deciseconds = deciseconds + (seconds * 10) + (minutes * 600)

        return total_deciseconds

    def deciseconds_to_minute(self, deciseconds):
        minutes = int(deciseconds / 600)
        seconds = int((deciseconds % 600) / 10)
        remain_deciseconds = deciseconds - (minutes * 600) - (seconds * 10)

        return f"{minutes}:{seconds}:{remain_deciseconds}"

    def scrap_f1_result(self, race_id):
        results = []
        formatted_results = []

        default_url = f"https://www.espn.com/f1/results/_/id/{race_id}"

        html_page = requests.get(default_url)
        beautiful_soup = BeautifulSoup(html_page.content, "html.parser")

        table_result = beautiful_soup.find("table", attrs={"class": "Table"})
        table_body_result = table_result.find("tbody")
        table_body_result_rows = table_body_result.find_all("tr")

        for row in table_body_result_rows:
            cols = row.find_all("td")
            cols = [element.text.strip() for element in cols]
            results.append([element for element in cols if element])

        race_leader_lap_time = None

        for (index, result) in enumerate(results):
            if index == 0: 
                race_leader_lap_time = result[3]

            object = {
                'position': "DNF" if result[0] == "Ret" else result[0],
                'driver'  : result[1][3:],
                'driver_nickname': result[1][:3],
                'team': result[2],
                'finished_laps': result[4],
                'pits': result[5],
                'race_leader_lap_time': race_leader_lap_time,
                'gap_to_race_leader': result[3] if index > 0 else None    
            }
            if index == 0:
                object['lap_time_in_deciseconds'] = self.get_total_deciseconds(
                    float(result[3].split(":")[2]), int(result[3].split(":")[1]), int(result[3].split(":")[0])
                )
            else:
                object['lap_time_in_deciseconds'] = self.get_total_deciseconds(
                    float(race_leader_lap_time.split(":")[2]), int(race_leader_lap_time.split(":")[1]), int(race_leader_lap_time.split(":")[0])
                )
                if result[3].find(":") == -1 and result[3].find("Lap") == -1:
                    object['lap_time_in_deciseconds'] = object['lap_time_in_deciseconds'] + float(result[3][1:])
                elif result[3].find(":") != -1:
                    object['lap_time_in_deciseconds'] = self.get_total_deciseconds(
                        float(race_leader_lap_time.split(":")[2]), int(race_leader_lap_time.split(":")[1]), int(race_leader_lap_time.split(":")[0])
                    ) + self.get_total_deciseconds(float(result[3].split(":")[1]), int(result[3].split(":")[0])) 

            formatted_results.append(object)

        for i in formatted_results:
            print(i)