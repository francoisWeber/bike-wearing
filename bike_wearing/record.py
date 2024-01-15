import json
import typer
from enum import Enum
from datetime import datetime, timedelta
from bike_wearing.weather import get_weather_at_time
import questionary
from loguru import logger

DATA_VERSION = 1
FNAME = "/Users/fweber/code/bike-wearing/records.json"


class Feeling(Enum):
    cool = "cold"
    ok = "ok"
    a_bit_hot = "a_bit_hot"
    hot = "hot"


class Moment(Enum):
    morning = "morning"
    evening = "evening"


first_layer_thickness = {
    "cotton": 1,
    "merino 100": 2,
    "merino 200": 3,
    "uniqlo heatech": 4,
}
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

app = typer.Typer(no_args_is_help=True)


def display_options_and_register():
    clothes2questions = {
        item[0]: questionary.select(message=item[0], choices=item[1].keys())
        for item in clothes_package
    }
    answers = questionary.form(**clothes2questions).ask()
    answer_numerical = {}
    for (cloth_name, value), (_, cloth_info) in zip(answers.items(), clothes_package):
        answer_numerical[cloth_name] = cloth_info[value]
    return answer_numerical


def record_clothing():
    infos = display_options_and_register()
    if len(infos) < len(clothes_package):
        logger.error("Incomplete input: aborting here")
        raise ValueError()
    return infos


# def record_weather(dtime: datetime):
#     timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
#     try:
#         weather_data = get_weather_at_time(dtime)
#         infos.update({"data_version": DATA_VERSION})
#         logger.info(f"Recorded {feeling=} for timestamp {timestamp}")
#         return infos
#     except ValueError:
#         logger.error(f"Error in weather fetching at {timestamp}")


# def ask_and_record(feeling: Feeling, dtime: datetime):
#     timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
#     infos["timestamp"] = timestamp
#     infos["feeling"] = feeling
#     infos = record_clothing(dtime)
#     weather_infos = record_weather(dtime)
#     infos.update(weather_infos)
#     infos["data_version"] = DATA_VERSION
#     with open(FNAME, "a+") as f:
#         f.write(json.dumps(infos) + "\n")


@app.command(name="record")
def record(
    moment: Moment,
    feeling: Feeling,
    copy_yesterday: bool = typer.Option(False, help="copy yesterday's values ?"),
):
    dtime = datetime.now()
    timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
    if moment == Moment.morning.value:
        dtime = dtime.replace(hour=8, minute=30)
    elif moment == Moment.evening.value:
        dtime = (dtime - timedelta(days=1)).replace(hour=18, minute=0)
    # start recording
    infos = {}
    # clothing
    if copy_yesterday:
        with open(FNAME, "r") as f:
            infos.update(json.loads(f.readline().strip()))
    else:
        infos.update(record_clothing())
    # weather
    infos.update(get_weather_at_time(dtime))
    # infos
    infos.update(
        {"timestamp": timestamp, "feeling": feeling.value, "data_version": DATA_VERSION}
    )
    # append to file
    with open(FNAME, "a+") as f:
        f.write(json.dumps(infos) + "\n")


# @app.command("evening")
# def evening(feeling: Feeling):
#     dtime = datetime.now()
#     dtime = (dtime - timedelta(days=1)).replace(hour=18, minute=0)
#     timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
#     logger.info(f"Recording feeling for YESTERDAY EVENING at {timestamp}")
#     try:
#         ask_and_record(feeling=feeling, dtime=dtime)
#     except:
#         logger.error("Recording failed: not logging anything")


# @app.command("morning")
# def morning(
#     feeling: Feeling,
#     copy_yesterday: bool = typer.Option("False", help="copy yesterday's values ?"),
# ):
#     dtime = datetime.now()
#     dtime = dtime.replace(hour=8, minute=30)
#     timestamp = dtime.strftime("%Y-%m-%dT%H-%M")
#     logger.info(f"Recording feeling for YESTERDAY EVENING at {timestamp}")
#     try:
#         ask_and_record(feeling=feeling, dtime=dtime)
#     except:
#         logger.error("Recording failed: not logging anything")


if __name__ == "__main__":
    app()
