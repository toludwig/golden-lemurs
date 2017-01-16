import asyncio
import websockets
import simplejson as json
from .rate_url import download_fields
from .networks.Ensemble import rebuild_full, ensemble_eval, cnn_eval
import tensorflow as tf


def start_eval_server():
    """
    Starts an evaluation Server that waits to receive a Url and returns an populated json object
    """

    async def consult(websocket, path):
        message = await websocket.recv()
        message = json.loads(message)
        repo = download_fields(message['Url'])
        repo["Category"] = cnn_eval([repo])[0].tolist()
        print(repo)
        print('\n')
        print(repo["Category"])
        await websocket.send(json.dumps(repo))

    with tf.Session() as session:
        rebuild_full()
        start_server = websockets.serve(consult, 'localhost', 8765)
        print('Started listening on localhost:8765')
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    start_eval_server()