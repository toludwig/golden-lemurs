import random
import simplejson as json
import re
from gensim.models.word2vec import Word2Vec
import numpy as np
import calendar as cal
from datetime import datetime
from os.path import join
from .. import DATA_DIR


class ExtensionVectorizer:

    def __init__(self):
       with open(join(DATA_DIR, 'extensions.json')) as f:
           self.extensions = json.load(f)

    def vectorize(self, repo):
        text = ""
        for file in repo['Files']:
            text += " " + file
        cleaned = clean_str(text).split()
        vector = np.zeros(len(self.extensions))
        for word in cleaned:
            try:
                index = self.extensions[word]
                vector[index] += 1
            except KeyError:
                pass
        return vector


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GloveWrapper(object, metaclass=Singleton):
    """Loads and manages the Word2vec Data"""

    def __init__(self):
        super(GloveWrapper, self).__init__()
        print('Loading GloVe-Vectors. This will take a while...', end='', flush=True)
        self.data = Word2Vec.load_word2vec_format(join(DATA_DIR, 'GoogleNews-vectors-negative300.bin'), binary=True)
        print('done.')

    def lookup_word(self, word):
        if word == '//pad//':
            return [0 for i in range(300)]
        try:
            return self.data[word]
        except Exception:
            return [0 for i in range(300)]

    def tokenize(self, text, length=200):
        tokens = clean_str(text).split()
        tokens += ['//pad//'] * (length - len(tokens))
        return [self.lookup_word(word) for word in tokens[:length]]


class TrainingData(object, metaclass=Singleton):
    """Manages the training data and provides batches."""
    def __init__(self):
        super(TrainingData, self).__init__()
        print('Constructing training data...', end='', flush=True)
        f1 = json.load(open(join(DATA_DIR, 'dev.json')))
        f6 = json.load(open(join(DATA_DIR, 'data.json')))
        f4 = json.load(open(join(DATA_DIR, 'docs.json')))
        f5 = json.load(open(join(DATA_DIR, 'web.json')))
        f3 = json.load(open(join(DATA_DIR, 'edu.json')))
        f2 = json.load(open(join(DATA_DIR, 'homework.json')))
        self.train = []
        self.val = []
        self.total_length = 0
        self.factors = []
        for cat in [f1, f2, f3, f4, f5, f6]:
            cut = int(len(cat) / 10)
            self.train += (cat[:-cut])
            self.val += cat[-cut:]
            temp = len(cat[:-cut])
            self.factors.append(temp)
            self.total_length += temp
        self.factors = list(map(lambda x: (1 / len(self.factors) / (x / self.total_length)), self.factors))
        print('done')

    def batch(self, size):
        indices = random.sample(range(len(self.train)), size)
        data = [self.train[index] for index in indices]
        random.shuffle(data)
        return data

    def validation(self, size):
        return [self.val[x:x+size] for x in range(0, len(self.val), size)]

    def full(self, size):
        combined = self.val + self.train
        indices = random.sample(range(len(combined)), size)
        data = [combined[index] for index in indices]
        random.shuffle(data)
        return data


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


def commit_time_profile(commit_times,
                        binsize=1,
                        period='month',
                        normed=False):
    '''
    From a list of commit times, make a histogram list with
    bins of size [1h | 2h | 3h | 4h | 6h | 12h | 1d | 2d | 3d]
    with respect to a period of one [week | month].
    Thus you get an activity profile of the period averaged over all times.
    If normed, the number of commits ber bin will be percentages.
    '''

    if 24 % binsize != 0:
        raise Exception('Invalid Binsize')

    times = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") for time in commit_times]

    days_per_period = 7 if period == 'week' else 31

    day_hour_matrix = np.zeros((days_per_period, 24))

    for time in times:
        if period == 'week':
            # get weekday
            month_day = time.day
            month = time.month
            year = time.year
            day = cal.weekday(year, month, month_day)
        elif period == 'month':
            day = time.day - 1  # days start at 1, but matrix at 0

        hour = time.hour
        # incrementing a cell in the matrix
        day_hour_matrix[day][hour] += 1

    indexes = range(int(24 / binsize))
    # summing over hours and/or days respectively
    data = []
    for day in day_hour_matrix:
        bins = []
        for index in indexes:
            bins.append(sum(day[(binsize * index):(binsize * index)+binsize]))
        if normed:
            bins_sum = np.sum(bins)
            bins = bins / bins_sum
        data.append(bins)
    data = sum(data, [])
    return data
