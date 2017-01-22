import asyncio
# import websockets
import simplejson as json
from .GitHelper import get_all
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
from flask import Flask
from flask_cors import CORS
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)


def start_eval_server():
    """
    Starts an evaluation Server that waits to receive a Url and returns an populated json object
    """
    server = Flask(__name__)
    CORS(server)

    @server.route('/data/<int:limit>')
    def data(limit):
        repos = []
        for file in ["data.json", "dev.json", "docs.json", "edu.json", "homework.json", "web.json"]:
            with open('data/%s' % file, 'r') as dataset:
                repos += json.load(dataset)
        data = np.random.choice(repos, limit).tolist()
        res = server.make_response(json.dumps(data))
        res.mimetype = 'application/json'
        return res

    def rating_to_category(rating):
        confidence = np.max(rating)
        if confidence < 0.2813: # no clear winner -> probably OTHER
            return '7'
        else:
            category = '%d' % (np.argmax(rating) + 1)
            return category

    @server.route('/rate/<name>/<title>/')
    def rate(name, title):
        logger.info('downloading %s/%s...' % (name, title))
        data = get_all(name, title, True)
        logger.info('evaluating %s/%s...' % (name, title))
        rating = ensemble_eval([data])[0].tolist()
        data['Category'] = rating_to_category(rating)
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
