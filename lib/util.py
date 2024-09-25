import string

import pulsectl
import spacy
from evdev import UInput, ecodes
from fasttext import FastText
from pulsectl import PulseSinkInfo
from lib import Config
import fasttext
from spacy import Language
from spacy.lang.en import STOP_WORDS

model: fasttext.FastText = None
# noinspection PyTypeChecker
nlp: Language = None
# noinspection PyTypeChecker
uinput: UInput = None
# noinspection PyTypeChecker
config: Config = None
def init(config_: Config):
    global model, nlp, uinput, config
    model = fasttext.load_model("model.bin")
    nlp = spacy.load("en_core_web_sm")
    uinput = UInput()
    config = config_

def predict(string: str):
    return model.predict(string)

def press_key(key: int):
    uinput.write(ecodes.EV_KEY, key, 1)
    uinput.write(ecodes.EV_KEY, key, 0)
    uinput.syn()

def get_active_sink(pulse: pulsectl.Pulse) -> PulseSinkInfo | None:
    sinks: list[PulseSinkInfo] = pulse.sink_list()
    for sink in sinks:
        if str(sink.state) == "<EnumValue sink/source-state=running>":
            return sink
    return None


def set_volume(vol: float, change = False):
    if vol > 1.0 or vol < -1.0:
        vol /= 100
    with pulsectl.Pulse() as pulse:
        active_sink = get_active_sink(pulse)
        if not active_sink:
            print("No active sink found.")
            return
        if change:
            current_volume = active_sink.volume.value_flat
            new_volume = max(min(current_volume + vol, 1.0), 0.0)
        else:
            new_volume = max(min(vol, 1.0), 0.0)
        pulse.volume_set_all_chans(active_sink, new_volume)
        # noinspection PyUnresolvedReferences
        print(f"Volume for {active_sink.description} set to {new_volume * 100:.0f}%")

def normalize_string(s):
    s = s.strip()
    if config.ignore_case:
        s = s.lower()
    if config.ignore_punctuation:
        s = s.translate(str.maketrans('', '', string.punctuation))
    if config.ignore_stopwords:
        s = " ".join([word for word in s.split() if word not in STOP_WORDS])
    return s

def parse_string(string: str):
    return nlp(string)