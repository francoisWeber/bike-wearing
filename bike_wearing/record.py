import typer
from enum import Enum
from datetime import datetime
from bike_wearing.weather import get_weather_at_time
import questionary
from loguru import logger


class Feeling(Enum):
    cool = "cold"
    ok = "ok"
    a_bit_hot = "a_bit_hot"
    hot = "hot"


first_layer_thickness = {"cotton": 1, "merino 100": 2, "merino 200": 3}
first_layer_slives = {"short": 1, "long": 2}
second_layer_thickness = {"no 2nd layer": 0, "fine": 1, "thick": 2}
jacket_thickness = {"no jacket": 0, "fine": 1, "thick": 2}
legs_merino = {"no leggin": 0, "merino": 1}
head_cover = {"simple helmet": 0, "earcached helmet": 1, "hood + helmet": 2}


clothes_package = [
    ("first_layer_thickness", first_layer_thickness),
    ("first_layer_slives", first_layer_slives),
    ("second_layer_thickness", second_layer_thickness),
    ("jacket_thickness", jacket_thickness),
    ("legs_merino", legs_merino),
    ("head_cover", head_cover),
]

app = typer.Typer()


def display_options_and_register():
    clothes2questions = {
        item[0]: questionary.select(message=item[0], choices=item[1].keys())
        for item in clothes_package
    }
    answers = questionary.form(**clothes2questions).ask()
    return answers


def record(feeling: str):
    dtime = datetime.now()
    timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
    infos = display_options_and_register()
    infos["timestamp"] = timestamp
    infos["feeling"] = feeling
    try:
        weather_data = get_weather_at_time(dtime)
        infos.update(weather_data)
        logger.info(f"Recorded {feeling=} for timestamp {timestamp}")
        return infos
    except ValueError:
        logger.error(f"Nothing recorded for timestamp {timestamp}")


@app.command("yesterday_evening")
def yesterday_evening(feeling: Feeling):
    print(feeling)


@app.command("this_morning")
def this_morning(feeling: Feeling):
    infos = record(feeling.value)
    print(infos)


if __name__ == "__main__":
    app()
