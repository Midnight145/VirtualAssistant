from dotenv import dotenv_values

from lib import Config, modules, util

config = Config(dotenv_values(".env"))
util.init(config)
module_map = {
    "askweather": modules.weather,
    "playpause": modules.MediaManager.play_pause,
    "raisevolume": lambda x: modules.MediaManager.change_volume(x, up=True),
    "lowervolume": lambda x: modules.MediaManager.change_volume(x, up=False),
    "stopplay": modules.MediaManager.stopplay,
    "settimer": modules.settimer,
    "setvolume": modules.MediaManager.set_volume,
    "tellmeabout": modules.tellmeabout,
    "searchweb": modules.searchweb
}

user_input = input("string: ")
prediction_text = util.normalize_string(user_input)
intents, confidence_scores = util.predict(prediction_text, 3)
prediction = intents[0]
print(f"Predicted intent {prediction} with confidence {confidence_scores[0]}")
intent = prediction[9::]
print(intent)
module_map[intent](user_input)