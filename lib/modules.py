import threading

import requests
from evdev import ecodes as e
from geopy import geocoders

from lib import util

gn = geocoders.Nominatim(user_agent="virtual-assistant-weather")

def weather(string: str):
    api = "https://api.tomorrow.io/v4/weather/forecast?location={}&apikey={}&units=imperial"

    parsed = util.parse_string(string)
    locs = [ent.text for ent in parsed.ents if ent.label_ == "GPE"]
    print(locs)
    if not locs:
        print("No location found.")
        return
    loc_str = " ".join(locs)
    # Tomorrow api for some reason won't actually accept the city name, so we have to get the lat/long
    # Unsure why, as the docs say it should accept city names
    # I've contacted them about it, will rewrite this if it gets resolved
    location = gn.geocode(loc_str)
    lat = location.latitude
    long = location.longitude
    loc = locs[0]
    resp = requests.get(api.format(f"{lat}, {long}", util.config.tomorrow_api_key), headers={"Accept": "application/json"})
    data = resp.json()
    print(data)
    if "tomorrow" in string:
        idx = 1

    else:
        idx = 0
    daily = data["timelines"]["daily"][idx]["values"]
    high = daily["temperatureMax"]
    low = daily["temperatureMin"]
    rainChance = daily["precipitationProbabilityAvg"]
    cloudy = daily["cloudCoverAvg"]

    print(f"{'Today' if idx == 0 else 'Tomorrow'} in {loc} the high will be {high}°F, the low will be {low}°F, there is a {rainChance}% chance of rain, and it will be {cloudy}% cloudy.")


class MediaManager:
    @staticmethod
    def play_pause():
        util.press_key(e.KEY_PLAYPAUSE)

    @staticmethod
    def previous_track():
        util.press_key(e.KEY_PREVIOUSSONG)

    @staticmethod
    def next_track():
        util.press_key(e.KEY_NEXTSONG)

    @staticmethod
    def stopplay():
        util.press_key(e.KEY_STOPCD)

    @staticmethod
    def change_volume(string: str, up: bool):
        parsed = util.parse_string(string)
        # will pull out all numbers from the string
        vol = [token.text for token in parsed if token.tag_ == "CD"]

        # if there's more than one number for some reason, we just assume the first number is correct
        if up:
            util.set_volume(int(vol[0]), change=True)
        else:
            util.set_volume(-int(vol[0]), change=True)

    @staticmethod
    def set_volume(string: str):
        parsed = util.parse_string(string)
        vol = [token.text for token in parsed if token.tag_ == "CD"]
        util.set_volume(int(vol[0]))

def settimer(user_input: str):
    parsed = util.parse_string(user_input)
    time_ = [ent.text for ent in parsed.ents if ent.label_ == "TIME"]
    if not time_:
        if time_ := util.extract_time_regex(user_input) is None:
            print("No time found.")
            return
    else:
        time_ = time_[0]
    thread = threading.Thread(target=util.set_timer, args=(time_,))
    thread.start()
    print(f"Timer set for {time_[0]}")