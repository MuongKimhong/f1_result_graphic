import requests
import os

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from bs4 import BeautifulSoup

from django.conf import settings


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
                    float(
                        race_leader_lap_time.split(":")[2]), 
                        int(race_leader_lap_time.split(":")[1]), 
                        int(race_leader_lap_time.split(":")[0])
                )
                if result[3].find(":") == -1 and result[3].find("Lap") == -1 and result[0] != 'Ret':   
                    object['lap_time_in_deciseconds'] = object['lap_time_in_deciseconds'] + float(result[3][1:])
                elif result[3].find(":") != -1:
                    object['lap_time_in_deciseconds'] = self.get_total_deciseconds(
                        float(race_leader_lap_time.split(":")[2]), 
                        int(race_leader_lap_time.split(":")[1]), 
                        int(race_leader_lap_time.split(":")[0])
                    ) + self.get_total_deciseconds(float(result[3].split(":")[1]), int(result[3].split(":")[0])) 

            formatted_results.append(object)

        return formatted_results


class Graphic:
    def __init__(self):
        self.graphic_width  = 1400
        self.graphic_height = 1400
        self.graphic_background = (108, 122, 137)

    def draw_laps(self, draw_object, total_laps, font):
        lap_position = 90
        lap_axis_length = self.graphic_width - (90 * 2)
        lap_gap = lap_axis_length / total_laps

        for i in range(total_laps):
            draw_object.line(
                (lap_position, 1310, lap_position, 1315), fill=(236, 240, 241), width=2
            )
            # draw number every 5 laps
            if i % 5 == 0:
                draw_object.text(
                    (lap_position - 2, 1325), f"{i + 1}", font=font, fill=(255, 255, 255)
                )
            lap_position = lap_position + lap_gap

        return lap_position

    def draw_drivers(self, blank_graphic, draw_object, race_results, lap_position):
        r = race_results
        r.reverse()

        driver_position = None

        for result in race_results[::-1]:
            if result['driver_nickname'] == 'HUL':
                driver_image = Image.open(
                    os.path.join(settings.BASE_DIR / f"assets/drivers/VET.png")
                )
            else:
                driver_image = Image.open(
                    os.path.join(settings.BASE_DIR / f"assets/drivers/{result['driver_nickname']}.png")
                )
            width  = driver_image.width
            height = driver_image.height

            new_width  = 230
            new_height = int((new_width * height) / width)

            driver_image = driver_image.resize((new_width, new_height), Image.ANTIALIAS)
            driver_image = driver_image.convert('RGBA')

            if driver_position is None:
                driver_position = 1310 - new_height            

            lap_length = 1400
            blank_graphic.paste(driver_image, (int(lap_position) - 200, int(driver_position) + 5), driver_image)
            driver_gap = (self.graphic_width - (90 * 2)) / 20
            driver_position = driver_position - driver_gap

    def draw_teams(self, blank_graphic, draw_object, race_results):
        total_drivers = 20
        team_axis_length = self.graphic_width - (90 * 2)
        team_gap = team_axis_length / total_drivers
        team_position = 1310

        r = race_results
        r.reverse()

        for result in r:
            if result['team'] == 'Ferrari':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/ferrariLogo.png')
                new_logo_width = 40
            elif result['team'] == 'Mercedes':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/mercLogo.png')
                new_logo_width = 50
            elif result['team'] == 'Haas':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/haasLogo.png')
                new_logo_width = 50
            elif result['team'] == 'Alfa Romeo':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/alfaromeoLogo.png')
                new_logo_width = 50
            elif result['team'] == 'Alpine':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/alpineLogo.png')
                new_logo_width = 50
            elif result['team'] == 'Aston Martin':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/astonmartinLogo.png')
                new_logo_width = 70
            elif result['team'] == 'McLaren':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/mclarenLogo.png')
                new_logo_width = 45
            elif result['team'] == 'Red Bull':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/redbullLogo.png')
                new_logo_width = 50
            elif result['team'] == 'Williams':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/williamLogo.png')
                new_logo_width = 45
            elif result['team'] == 'AlphaTauri':
                team_logo_path = os.path.join(settings.BASE_DIR / 'assets/alphatauriLogo.png')
                new_logo_width = 50

            team_logo = Image.open(team_logo_path)
            team_logo_width  = team_logo.width
            team_logo_height = team_logo.height

            new_logo_height = int((new_logo_width * team_logo_height) / team_logo_width)
            new_team_logo = team_logo.resize((new_logo_width, new_logo_height), Image.ANTIALIAS)
            new_team_logo = new_team_logo.convert('RGBA')

            draw_object.line((85, team_position, 1400 - 90, team_position), fill=(236, 240, 241), width=2)
            blank_graphic.paste(new_team_logo, (16, int(team_position - new_logo_height - 5)), new_team_logo)
            team_position = team_position - team_gap  

    def generate_graphic(self, race_results):
        blank_graphic = Image.new(
            'RGB', (self.graphic_width, self.graphic_height), self.graphic_background
        )
        draw_object = ImageDraw.Draw(blank_graphic)
        font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'assets/font.TTF'), 16)

        # draw x y coordinate
        draw_object.line((90, 90, 90, 1310), fill=(255, 76, 48), width=5)
        draw_object.line((90, 1310, 1310, 1310), fill=(255, 76, 48), width=5)

        # draw lap number on coordinate
        total_laps = int(race_results[0]['finished_laps'])
        lap_position = self.draw_laps(draw_object, total_laps, font)
        self.draw_teams(blank_graphic, draw_object, race_results)
        self.draw_drivers(blank_graphic, draw_object, race_results, lap_position)

        blank_graphic.show()
