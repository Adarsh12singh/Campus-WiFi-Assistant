import json
import os


CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config.json"
)


def get_config():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:

        return json.load(file)


def get_value(key):

    return get_config().get(key)