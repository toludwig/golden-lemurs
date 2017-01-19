import random
import simplejson as json
import re
from gensim.models.word2vec import Word2Vec
import numpy as np
import calendar as cal
from datetime import datetime
from os.path import join
from classification import DATA_DIR
import logging


logger = logging.getLogger(__name__)

Word2Vec_PATH = join(DATA_DIR, 'GoogleNews-vectors-negative300.bin')


class ExtensionVectorizer:
    """
    Uses a list of extensions to create a bog of words vector from text
    """
    def __init__(self):
        with open(join(DATA_DIR, 'extensions.json')) as f:
            self.extensions = json.load(f)

    def vectorize(self, repo):
        """
        get the vector representation of the files of this repo
        :param repo: the repo to vectorize
        :return: a vector of length 300 where every index is a word and the value is its frequency
        """
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
                logger.debug("Word %s not found" % word)
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
        try:
            self.data = Word2Vec.load_word2vec_format(Word2Vec_PATH, binary=True)
        except FileNotFoundError:
            logger.exception('Could not find Word2Vec data at %s' % Word2Vec_PATH)
            raise
        print('done.')

    def lookup_word(self, word):
        """
        return the vector representation of a word. falls back to a zero vector if no match was found
        :param word: the word to lookup
        :return: the vector representation
        """
        if word == '//pad//':
            return [0 for i in range(300)]
        try:
            return self.data[word]
        except Exception:
            logger.debug("Word %s not found" % word)
            return [0 for i in range(300)]

    def tokenize(self, text, length=200):
        """
        transforms a text to vector representations up to a max length. shorter texts are padded
        :param text: the text to vectorize
        :param length: the max length
        :return: a list of vectors
        """
        tokens = clean_str(text).split()
        tokens += ['//pad//'] * (length - len(tokens))
        return [self.lookup_word(word) for word in tokens[:length]]


class TrainingData(object, metaclass=Singleton):
    """Manages the training data and provides batches."""
    def __init__(self):
        super(TrainingData, self).__init__()
        print('Constructing training data...', end='', flush=True)
        try:
            f1 = json.load(open(join(DATA_DIR, 'dev.json')))
            f6 = json.load(open(join(DATA_DIR, 'data.json')))
            f4 = json.load(open(join(DATA_DIR, 'docs.json')))
            f5 = json.load(open(join(DATA_DIR, 'web.json')))
            f3 = json.load(open(join(DATA_DIR, 'edu.json')))
            f2 = json.load(open(join(DATA_DIR, 'homework.json')))
        except FileNotFoundError:
            logger.exception("Could not find training data in %s" % DATA_DIR)
            raise
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
        """
        Provides a batch of Trainingdata
        :param size: size of batch
        :return: the batch
        """
        indices = random.sample(range(len(self.train)), size)
        data = [self.train[index] for index in indices]
        random.shuffle(data)
        return data

    def validation(self, size):
        """
        returns the entire validation data as sublists
        :param size: length of sublists
        :return: the validation data
        """
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
    bins of size binsize
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
