import tensorflow as tf
from ..Logger import Logger
from ..Data import TrainingData, GloveWrapper, Extension_Vectorizer
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from ..NumericFFN.NumericFFN import NumericFFN
from ..Training import train, validate, TrainingData
from .settings import *
import re


VAL_SIZE = 50
SAVE_INTERVAL = 20
CHECKPOINT_PATH = "out/CNN"
NETWORK_PATH = 'classification/networks/GlovedCNN/TextCNN.py'
TITLE = 'TextCNN'
COMMENT = """sequence_length=%d
        filter_sizes=%s
        num_filters=%d
        num_batches=%d
        batch_size=%d
        learning rate=%f
        neurons_hidden=%s
""" % (SEQUENCE_LENGTH, FILTER_SIZES, NUM_FILTERS, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE, NEURONS_HIDDEN)


def main():
    net = NumericFFN(Parameters, NEURONS_HIDDEN, 6, LEARNING_RATE, L2_REG)

    vectorizer = Extension_Vectorizer()

    logger = Logger(TITLE, COMMENT)
    logger.set_source(NETWORK_PATH)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('dropout_keep_prop', net.dropout_keep_prob)
            tf.add_to_collection('scores', net.scores)
            tf.add_to_collection('predictions', net.predictions)

        def train_step(in_batch, target_batch):
            feed_dict = {
                net.in_vector: in_batch,
                net.target_vect: target_batch,
                net.dropout_keep_prob: 0.5,
                net.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([net.train_op, net.accuracy, net.loss, net.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                net.in_vector: in_batch,
                net.target_vect: target_batch,
                net.dropout_keep_prob: 1.0
            }
            acc = session.run(net.accuracy, feed_dict)
            return acc

        train(train_step, vectorizer.vectorize, NUM_BATCHES,
              BATCH_SIZE, collection_hook, logger, CHECKPOINT_PATH)

        validate(val_step, vectorizer.vectorize, VAL_SIZE, logger)


if __name__ == '__main__':
    main()