import datetime
import re
import string
import time
from collections import Counter
from heapq import nlargest

import fasttext
import notify2
import pulsectl
import requests
import spacy
import wikipediaapi
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
wiki_api: wikipediaapi.Wikipedia
def init(config_: Config):
    global model, nlp, uinput, config, wiki_api
    wiki_api = wikipediaapi.Wikipedia('virtual-assistant')
    model = fasttext.load_model(config_.model)
    nlp = spacy.load("en_core_web_sm")
    uinput = UInput()
    config = config_

def predict(string: str, k: int = 1):
    # Realistically this doesn't need to be its own function, but we want all of the heavy lifting here and have main be just the driver file
    return model.predict(string, k=k)

def extract_subject(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART"]:  # Add more relevant entity types
            return ent.text
    # Fallback - if no entity found, use the entire input as the subject
    return text

def search_wikipedia(topic):
    page = wiki_api.page(topic)
    if page.exists():
        return page
    else:
        return None

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
    time_ = time_.split(":")
    hours = int(time_[0])
    minutes = int(time_[1])
    target_time = current_time.replace(hour=hours + 12 if current_time.hour > hours else hours, minute=minutes, second=0, microsecond=0)
    delta = target_time - current_time
    print(delta.total_seconds())
    time.sleep(delta.total_seconds())
    notify2.init("Virtual Assistant")
    notify2.Notification(f"Timer from {current_time.strftime('%I:%M %p')} has finished.", "Time's up!").show()

def search_google(query: str):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={config.google_api_key}&cx={config.cse_id}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        if results:
            return results[0]['snippet']  # Return the first result snippet
    return None

def summarize(string: str):
    doc = nlp(string)
    keyword = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']
    for token in doc:
        if token.text in STOP_WORDS or token.is_punct:
            continue
        if token.pos_ in pos_tag:
            keyword.append(token.text)
    freq_word = Counter(keyword)
    max_freq = Counter(keyword).most_common(1)[0][1]
    for word in freq_word.keys():
        freq_word[word] = (freq_word[word] / max_freq)

    sent_strength = {}
    for sent in doc.sents:
        for word in sent:
            if word.text in freq_word.keys():
                if sent in sent_strength.keys():
                    sent_strength[sent] += freq_word[word.text]
                else:
                    sent_strength[sent] = freq_word[word.text]

    summarized_sentences = nlargest(3, sent_strength, key=sent_strength.get)
    final_sentences = [w.text for w in summarized_sentences]
    return ' '.join(final_sentences)