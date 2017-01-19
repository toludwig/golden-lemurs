import simplejson as json
from .GitHelper import fetch_repo
from .rate_url import split_url
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)

# stdout is output file

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def classify():
    """
    Reads urls separated by newlines from stdin and writes urls and classifications to stdout
    """
    def rate(name, title):
        logger.info('downloading %s/%s...' % (name, title))
        data = fetch_repo(name, title)
        logger.info('evaluating %s/%s...' % (name, title))
        rating = ensemble_eval([data])[0].tolist()
        # ensemble gives us probabilities for each category, maximise this
        category = np.argmax(rating)
        logger.info('result for %s/%s: %s' % (name, title, rating))
        tags = ["DEV", "HW", "EDU", "DOCS", "WEB", "DATA", "OTHER"]
        return tags[category]

    with tf.Session() as session:
        rebuild_full()
        for url in sys.stdin:
            name, title = split_url(url[:-1])
            category = rate(name, title)
            print('%s %s' % (url[:-1], category))


if __name__ == '__main__':
    classify()
