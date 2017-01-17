import asyncio
# import websockets
import simplejson as json
from .rate_url import download_fields, enrich_entry
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
from flask import Flask
app = Flask(__name__)
import sys
import logging

@app.route('/')
def hello_world():
    return 'Hello, World!'
logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def start_eval_server():
    """
    Starts an evaluation Server that waits to receive a Url and returns an populated json object
    """
    server = Flask(__name__)

    async def consult(websocket, path):
        message = await websocket.recv()
        message = json.loads(message)
        repo = enrich_entry(message, download_fields)
        logger.info('evaluating %s...' % repo)
        repo["Category"] = ensemble_eval([repo])[0].tolist()
        logger.info('result for %s: %s' % (repo['Url'], repo["Category"]))
        await websocket.send(json.dumps(repo))

    with tf.Session() as session:
        rebuild_full()
        start_server = server.run()


if __name__ == '__main__':
    start_eval_server()
