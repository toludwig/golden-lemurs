import asyncio
# import websockets
import simplejson as json
from .rate_url import download_fields
from .networks.Ensemble import rebuild_full, ensemble_eval
import tensorflow as tf
import time
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def retryUntilTimeout(function):
    def f(*args, **kwargs):
        timeout = time.time() + 60
        while True:
            if time.time() > timeout:
                raise Exception("Unable to get repo.")
            try:
                result = function(*args, **kwargs)
                if result is not None:
                    return result
            except Exception:
                time.sleep(0.5)


def start_eval_server():
    """
    Starts an evaluation Server that waits to receive a Url and returns an populated json object
    """
    server = Flask(__name__)

    @server.route('rate/<path:repo>')
    def consult(repo):
        data = download_fields(repo)
        data["Category"] = ensemble_eval([data])[0].tolist()
        print(data)
        print('\n')
        print(data["Category"])
        return json.dumps(repo)

    with tf.Session() as session:
        rebuild_full()
        start_server = server.run()


if __name__ == '__main__':
    start_eval_server()
