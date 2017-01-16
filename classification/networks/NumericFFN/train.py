import tensorflow as tf
from ..Logger import Logger
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .NumericFFN import NumericFFN
from ..Data import TrainingData
from ..Training import train, validate
from .settings import *

VAL_SIZE = 50
SAVE_INTERVAL = 20
NETWORK_PATH = 'classification/networks/NumericFFN/NumericFFN.py'
TITLE = 'FFN'
COMMENT = """neurons_hidden=%s
        num_batches=%d
        batch_size=%d
        learning rate=%f
""" % (NEURONS_HIDDEN, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE)

CHECKPOINT_PATH = "out/FFN"


def preprocess(x):
    data = []
    for key in FEATURES:
        data.append(x[key])
    return data


def main():
    ffn = NumericFFN(parameters=len(FEATURES),
                     neurons_hidden=NEURONS_HIDDEN,
                     categories=6,
                     learning_rate=LEARNING_RATE,
                     reg_lambda=0.01)

    logger = Logger(TITLE, COMMENT)
    logger.set_source(NETWORK_PATH)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('score', ffn.scores)
            tf.add_to_collection('input', ffn.in_vector)
            tf.add_to_collection('dropout_keep_prop', ffn.dropout_keep_prob)
            tf.add_to_collection('predictions', ffn.predictions)
            tf.add_to_collection('category', ffn.category)

        def train_step(in_batch, target_batch):
            feed_dict = {
                ffn.in_vector: in_batch,
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 0.5,
                ffn.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([ffn.train_op, ffn.accuracy, ffn.loss, ffn.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                ffn.in_vector: in_batch,
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 1.0
            }
            acc = session.run(ffn.accuracy, feed_dict)
            return acc

        train(train_step,
              preprocess,
              NUM_BATCHES,
              BATCH_SIZE,
              collection_hook,
              logger,
              CHECKPOINT_PATH,
              name='FFN',
              full=True)

        validate(val_step, preprocess, BATCH_SIZE, logger)


if __name__ == '__main__':
    main()
