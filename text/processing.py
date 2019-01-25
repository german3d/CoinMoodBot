import re
import datetime
import emoji
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from text.contractions import contractions_dict
from config import CRYPTO_INFO


# List of hashtags and mentions for all crypto assets
NAMES = [name for asset in CRYPTO_INFO.values() for name in asset]

# WordNet NLTK lemmatizer
lemmatizer = WordNetLemmatizer()


class TweetProcessor:
    def __init__(self, text):        
        self.text = text

    def remove_spaces(self):
        self.text = re.sub(pattern="\s+", repl=" ", string=self.text)

    def remove_amps(self):
        self.text = re.sub(pattern="&amp", repl="", string=self.text)

    def capture_urls(self):
        pat = "http[s]?:[/]?[/]?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        self.text = re.sub(pattern=pat, repl=" url ", string=self.text)
    
    def remove_hashtags(self):
        self.text = re.sub(pattern=r"#(\w+)", repl="", string=self.text)
        
    def remove_mentions(self):
        self.text = re.sub(pattern=r"@(\w+)", repl="", string=self.text)

    def remove_ending(self):
        self.text = re.sub(pattern=r"(\w+)?…", repl=" ", string=self.text.rstrip())

    def remove_ordinal_prefix(self):
        self.text = re.sub(pattern=r"(?<=\d)(st|nd|rd|th)\b", repl="", string=self.text)

    def capture_numbers(self):
        self.text = re.sub(pattern=r"\d+(?:[\d,.]*\d)?", repl=" num ", string=self.text)

    def capture_punctuation(self):
        repl_dict = {"!": " exclm ",
                     "?": " qstn "}
        regex = re.compile("(%s)" % "|".join(map(re.escape, repl_dict.keys())))
        self.text = regex.sub(lambda x: repl_dict[x.string[x.start(): x.end()]], self.text)

    def replace_contractions(self):
        regex = re.compile("(%s)" % "|".join(map(re.escape, contractions_dict.keys())))
        self.text = regex.sub(lambda x: contractions_dict[x.string[x.start(): x.end()]], self.text)

    def remove_dollars(self):
        self.text = re.sub(pattern=r"$(\w+)", repl="", string=self.text)

    def remove_punctuation(self):
        repl_dict = str.maketrans({key: "" for key in r"!\"#$%&\'’()*+,-./:;<=>?@[\\]^_`{|}~"})
        self.text = self.text.translate(repl_dict)

    def remove_names(self):
        regex = re.compile("(%s)" % "|".join(map(re.escape, NAMES)), flags=re.I)
        self.text = regex.sub(lambda x: " ", self.text)

    def remove_singletons(self):
        self.text = re.sub(pattern=r"\b\w\b", repl=" ", string=self.text)

    def get_lemmas(self):
        def _get_wordnet_pos(treebank_tag):
            if treebank_tag.startswith('J'):
                return wordnet.ADJ
            elif treebank_tag.startswith('V'):
                return wordnet.VERB
            elif treebank_tag.startswith('N'):
                return wordnet.NOUN
            elif treebank_tag.startswith('R'):
                return wordnet.ADV
            else:
                return 'n'
        tokens = self.text.lower().split()
        pos_treebank = [pair[1] for pair in pos_tag(tokens)]
        pos_wordnet = list(map(_get_wordnet_pos, pos_treebank))
        lemmas = [lemmatizer.lemmatize(word, pos) for word, pos in zip(tokens, pos_wordnet)]
        self.text = " ".join(lemmas)

    def convert_emoji(self):
        self.text = emoji.demojize(self.text, delimiters=(" :", ": "))

    def join_tokens(self):
        self.text = " ".join(self.text.split())

    def process_text(self):
        self.remove_spaces()
        self.remove_amps()
        self.capture_urls()
        self.remove_hashtags()
        self.remove_mentions()        
        self.replace_contractions()
        self.remove_names()
        self.remove_ordinal_prefix()
        self.capture_numbers()
        self.capture_punctuation()
        self.remove_dollars()
        self.remove_punctuation()
        self.remove_ending()
        self.remove_singletons()
        self.get_lemmas()
        self.convert_emoji()
        self.join_tokens()        


class TweetChecker:
    def __init__(self, date):
        self.max_id = 0
        self.min_id = 1e30
        self.date = date
        self.start_timestamp = datetime.datetime.combine(date, datetime.time(0,0))

    def update(tweet_id):
        if tweet_id > self.max_id:
            self.max_id = tweet_id
        if tweet_id < self.min_id:
            self.min_id = tweet_id

    def check_timestamp(self, ts):
        return ts >= self.start_timestamp
