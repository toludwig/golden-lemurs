#!/usr/bin/env python
import tensorflow as tf
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
from classification.networks.Logger import Logger
from classification.networks.Data import ExtensionVectorizer
from classification.networks.NumericFFN.NumericFFN import NumericFFN
from classification.networks.Training import train, validate, TrainingData


TRAIN_ON_FULL_DATA = False

NUM_EXTENSIONS = 300
BATCH_SIZE = 200
NUM_BATCHES = 300
LEARNING_RATE = 1e-3
NEURONS_HIDDEN = [100, 100]
L2_REG = 0.01
Parameters = 300

SAVE_INTERVAL = 20
CHECKPOINT_PATH = "../../out/Files"
NETWORK_PATH = '../../classification/networks/NumericFFN/NumericFFN.py'
TITLE = 'FFN'
COMMENT = """neurons_hidden=%s
        num_batches=%d
        batch_size=%d
        learning rate=%f
""" % (NEURONS_HIDDEN, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE)


def main():
    net = NumericFFN(parameters=NUM_EXTENSIONS,
                     neurons_hidden=NEURONS_HIDDEN,
                     categories=6,
                     learning_rate=LEARNING_RATE,
                     reg_lambda=L2_REG)

    vectorizer = ExtensionVectorizer()

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

        train(training_step=train_step,
              preprocess=vectorizer.vectorize,
              num_batches=NUM_BATCHES,
              batch_size=BATCH_SIZE,
              collection_hook=collection_hook,
              logger=logger,
              checkpoint_path=CHECKPOINT_PATH,
              name=TITLE,
              full=TRAIN_ON_FULL_DATA)

        if not TRAIN_ON_FULL_DATA:
            validate(validation_step=val_step,
                     preprocess=vectorizer.vectorize,
                     batch_size=BATCH_SIZE,
                     logger=logger)

if __name__ == '__main__':
    main()