import asyncio
# import websockets
import simplejson as json
from .GitHelper import fetch_repo
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
from flask import Flask
import sys
import logging

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

    @server.route('/rate/<name>/<title>/')
    def rate(name, title):
        logger.info('downloading %s/%s...' % (name, title))
        data = fetch_repo(name, title)
        logger.info('evaluating %s/%s...' % (name, title))
        data["Category"] = ensemble_eval([data])[0].tolist()
        logger.info('result for %s/%s: %s' % (name, title, data["Category"]))
        res = server.make_response(json.dumps(data))
        res.mimetype = 'application/json'
        return res


    # async def consult(websocket, path):
    #     message = await websocket.recv()
    #     message = json.loads(message)
    #     repo = enrich_entry(message, download_fields)
    #     logger.info('evaluating %s...' % repo)
    #     repo["Category"] = ensemble_eval([repo])[0].tolist()
    #     logger.info('result for %s: %s' % (repo['Url'], repo["Category"]))
    #     await websocket.send(json.dumps(repo))

    with tf.Session() as session:
        rebuild_full()
        print("Starting server...", end='\t')
        server.run(host='0.0.0.0', port=8081)
        print("Done.")


if __name__ == '__main__':
    start_eval_server()
