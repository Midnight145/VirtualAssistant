from evdev import ecodes as e

from lib import util


def weather(string: str):
    parsed = util.parse_string(string)
    locs = [ent.text for ent in parsed.ents if ent.label_ == "GPE"]
    print(locs)
# https://www.tomorrow.io/weather-api/  # API for weather data

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
        vol = [token.text for token in parsed if token.tag_ == "CD"]

        if up:
            util.set_volume(int(vol[0]), change=True)
        else:
            util.set_volume(-int(vol[0]), change=True)

    @staticmethod
    def set_volume(string: str):
        parsed = util.parse_string(string)
        vol = [token.text for token in parsed if token.tag_ == "CD"]
        util.set_volume(int(vol[0]))