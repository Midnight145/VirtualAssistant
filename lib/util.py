import datetime
import string
import time
import re

import fasttext
import notify2
import pulsectl
import spacy

from evdev import UInput, ecodes
from pulsectl import PulseSinkInfo
from spacy import Language
from spacy.lang.en import STOP_WORDS
from spacy.tokens import Doc

from lib import Config

model: fasttext.FastText
nlp: Language
uinput: UInput
config: Config

def init(config_: Config):
    global model, nlp, uinput, config
    model = fasttext.load_model("model.bin")
    nlp = spacy.load("en_core_web_sm")
    uinput = UInput()
    config = config_

def predict(string: str):
    # Realistically this doesn't need to be it's own function, but we want all of the heavy lifting here and have main be just the driver file
    return model.predict(string)

def press_key(key: int):
    uinput.write(ecodes.EV_KEY, key, 1)
    uinput.write(ecodes.EV_KEY, key, 0)
    uinput.syn()

def get_active_sink(pulse: pulsectl.Pulse) -> PulseSinkInfo | None:
    """
    :param pulse: the Pulse object
    :return: The first active sink
    """
    sinks: list[PulseSinkInfo] = pulse.sink_list()
    for sink in sinks:
        # This is super hacky. If there's currently no audio playing through the sink, even if it's the one selected, it won't be detected.
        if str(sink.state) == "<EnumValue sink/source-state=running>":
            return sink
    return None

def set_volume(vol: float, change = False):
    if vol > 1.0 or vol < -1.0: # for like, 55 instead of .55
        vol /= 100
    with pulsectl.Pulse() as pulse:
        active_sink = get_active_sink(pulse)
        if not active_sink:
            print("No active sink found.")
            return
        if change:
            current_volume = active_sink.volume.value_flat
            new_volume = max(min(current_volume + vol, 1.0), 0.0) # clamp vol between 0 and 1
        else:
            new_volume = max(min(vol, 1.0), 0.0)
        pulse.volume_set_all_chans(active_sink, new_volume)
        # noinspection PyUnresolvedReferences
        print(f"Volume for {active_sink.description} set to {new_volume * 100:.0f}%")

def normalize_string(s: str) -> str:
    """
    This will normalize a string into the same format that was trained by the model, using the values in .env
    :param s: the string to normalize
    :return: the normalized string
    """
    s = s.strip()  # we don't want the trailing newline
    if config.ignore_case:
        s = s.lower()
    if config.ignore_punctuation:
        s = s.translate(str.maketrans('', '', string.punctuation))
    if config.ignore_stopwords:
        s = " ".join([word for word in s.split() if word not in STOP_WORDS])
    return s

def parse_string(string_: str) -> Doc:
    return nlp(string_)


def extract_time_regex(text: str):
    # Regex pattern to match time in the format HH:MM
    time_pattern = r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\b'
    match = re.search(time_pattern, text)
    if match:
        return match.group()
    return None


def set_timer(time_: str):
    current_time = datetime.datetime.now()
    print(time_)
    time_ = time_.split(":")
    print("split:",time_)
    hours = int(time_[0])
    minutes = int(time_[1])
    target_time = current_time.replace(hour=hours + 12 if current_time.hour > hours else hours, minute=minutes, second=0, microsecond=0)
    delta = target_time - current_time
    print(delta.total_seconds())
    time.sleep(delta.total_seconds())
    notify2.init("Virtual Assistant")
    notify2.Notification("Timer", "Time's up!", "notification-message-im").show()