class Config:
    def __init__(self, env):
        self.add_label = True if env.get("ADD_LABEL", False) == "true" else False
        self.epoch =int(env.get("EPOCH", 25))
        self.learning_rate = float(env.get("LEARNING_RATE", 0.5))
        self.ngrams = int(env.get("NGRAMS", 2))
        self.ignore_case = True if env.get("IGNORE_CASE", False) == "true" else False
        self.ignore_punctuation = True if env.get("IGNORE_PUNCTUATION", False) == "true" else False
        self.ignore_stopwords = True if env.get("IGNORE_STOPWORDS", False) == "true" else False
        if "MODEL" not in env:
            raise ValueError("MODEL variable not set.")
        self.model = env.get("MODEL")
        self.tomorrow_api_key = env.get("TOMORROW_API_KEY")
        self.google_api_key = env.get("GOOGLE_API_KEY")
        self.cse_id = env.get("CSE_ID")