from dotenv import dotenv_values
from lib import Config, modules, util

config = Config(dotenv_values())
util.init(config)

user_input = "Lower the volume by 10%"
prediction_text = util.normalize_string(user_input)
prediction = util.predict(prediction_text)
print(prediction)
if prediction[0][0] == "__label__askweather":
    modules.weather("What is the weather in Denton, Texas?")
elif prediction[0][0] == "__label__play":
    modules.MediaManager.play_pause()
elif prediction[0][0] == "__label__pause":
    modules.MediaManager.play_pause()
elif prediction[0][0] == "__label__raisevolume":
    modules.MediaManager.change_volume(user_input, up=True)
elif prediction[0][0] == "__label__lowervolume":
    modules.MediaManager.change_volume(user_input, up=False)
elif prediction[0][0] == "__label__stopplay":
    modules.MediaManager.stopplay()


