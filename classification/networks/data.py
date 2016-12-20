import numpy as np
import pandas

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Data(object, metaclass=Singleton):
    """Singleton that loads the GloVe Data"""
    def __init__(self):
        super(Data, self).__init__()
        print('Loading GloVe-Vectors. This will take a while...')
        self.data = pandas.read_csv('./data/glove.42B.300d.txt', delim_whitespace=True, error_bad_lines=False)
