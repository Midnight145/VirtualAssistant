class Config:
    def __init__(self, env):
        self.epoch = env.get("EPOCH", 25)
        self.learning_rate = env.get("LEARNING_RATE", 0.5)
        self.ngrams = env.get("NGRAMS", 2)
        self.ignore_case = env.get("IGNORE_CASE", False)
        self.ignore_punctuation = env.get("IGNORE_PUNCTUATION", False)
        self.ignore_stopwords = env.get("IGNORE_STOPWORDS", False)
        if "MODEL" not in env:
            raise ValueError("MODEL variable not set.")
        self.model = env.get("MODEL")