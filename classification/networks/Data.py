import random
import math
import simplejson as json
import re
from gensim.models.word2vec import Word2Vec


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GloveWrapper(object, metaclass=Singleton):
    """Singleton that loads the GloVe Data"""

    def __init__(self):
        super(GloveWrapper, self).__init__()
        print('Loading GloVe-Vectors. This will take a while...', end='', flush=True)
        self.data = Word2Vec.load_word2vec_format('data/GoogleNews-vectors-negative300.bin', binary=True)
        print('done.')

    def lookup_word(self, word):
        if word == '//pad//':
            return [0 for i in range(300)]
        try:
            return self.data[word]
        except:
            return [0 for i in range(300)]

    def tokenize(self, text, length=200):
        # todo: padding
        tokens = clean_str(text).split()
        tokens += ['//pad//'] * (length - len(tokens))
        return [self.lookup_word(word) for word in tokens[:length]]


class TrainingData(object, metaclass=Singleton):
    """Manages the training data and provides batches."""
    def __init__(self):
        super(TrainingData, self).__init__()
        print('Constructing training data...', end='', flush=True)
        f1 = json.load(open('data/dev_full.json'))
        f2 = json.load(open('data/data_full.json'))
        f3 = json.load(open('data/docs_full.json'))
        f4 = json.load(open('data/web_full.json'))
        f5 = json.load(open('data/edu_full.json'))
        f6 = json.load(open('data/homework_full.json'))
        self.cats = []
        self.val = []
        for cat in [f1, f2, f3, f4, f5, f6]:
            self.cats.append(cat[:-500])
            self.val += cat[-500:]
        print('done')

    def batch(self, size):
        num_entries = math.floor(size / len(self.cats))

        data = []
        for entry in self.cats:
            indices = random.sample(range(len(entry)), num_entries)
            data += [entry[index] for index in indices]
        random.shuffle(data)
        return data

    def validation(self, size):
        return [self.val[x:x+size] for x in range(0, len(self.val), size)]


def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " ", string)
    string = re.sub(r"\)", " ", string)
    string = re.sub(r"\?", " ", string)
    string = re.sub(r"\"", " ", string)
    string = re.sub(r"`", " ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()
