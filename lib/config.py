class Config:
    def __init__(self, env):
        self.epoch =int(env.get("EPOCH", 25))
        self.learning_rate = float(env.get("LEARNING_RATE", 0.5))
        self.ngrams = int(env.get("NGRAMS", 2))
        self.ignore_case = bool(env.get("IGNORE_CASE", False))
        self.ignore_punctuation = bool(env.get("IGNORE_PUNCTUATION", False))
        self.ignore_stopwords = bool(env.get("IGNORE_STOPWORDS", False))
        if "MODEL" not in env:
            raise ValueError("MODEL variable not set.")
        self.model = env.get("MODEL")
        self.tomorrow_api_key = env.get("TOMORROW_API_KEY")