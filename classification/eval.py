import asyncio
# import websockets
import simplejson as json
from .GitHelper import fetch_repo
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
from flask import Flask
from flask_cors import CORS
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def start_eval_server():
    """
    Starts an evaluation Server that waits to receive a Url and returns an populated json object
    """
    server = Flask(__name__)
    CORS(server)

    @server.route('/rate/<name>/<title>/')
    def rate(name, title):
        logger.info('downloading %s/%s...' % (name, title))
        data = fetch_repo(name, title)
        logger.info('evaluating %s/%s...' % (name, title))
        rating = ensemble_eval([data])[0].tolist()
        data['Category'] = '%d' % (np.argmax(rating) + 1)
        data['Rating'] = rating
        logger.info('result for %s/%s: %s' % (name, title, rating))
        res = server.make_response(json.dumps(data))
        res.mimetype = 'application/json'
        return res

    with tf.Session() as session:
        rebuild_full()
        print("Starting server...", end='\t')
        server.run(host='0.0.0.0', port=8081)
        print("Done.")


if __name__ == '__main__':
    start_eval_server()
