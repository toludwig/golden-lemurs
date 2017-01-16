#!/usr/bin/env python
import os
import sys

import tensorflow as tf

sys.path.insert(0, os.path.abspath('../..'))
from classification.Logger import Logger
from classification.Data import commit_time_profile
from classification.networks.LSTM import LSTM
from classification.Training import train, validate, TrainingData


LEARNING_RATE = 1e-3
NUM_LAYERS = 3
NUM_BATCHES = 500
BATCH_SIZE = 120
SERIES_LENGTH = 744
NEURONS_HIDDEN = 100


SAVE_INTERVAL = 200
TITLE = 'RNN'
COMMENT = """learning_rate=%f
             num_layers=%d
             num_batches=%d
             batch_size=%d
             series_length=%d
             neurons_hidden=%d
""" % (LEARNING_RATE, NUM_LAYERS, NUM_BATCHES, BATCH_SIZE, SERIES_LENGTH, NEURONS_HIDDEN)


def preprocess(x):
    return commit_time_profile(x['CommitTimes'])


def main():
    rnn = LSTM(NUM_LAYERS, NEURONS_HIDDEN, 6, SERIES_LENGTH, LEARNING_RATE)

    logger = Logger(TITLE, COMMENT)
    logger.set_source(rnn)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('features', rnn.lstm)
            tf.add_to_collection('input', rnn.input_vect)
            tf.add_to_collection('dropout_keep_prop', rnn.dropout_keep_prob)
            tf.add_to_collection('batch_size', rnn.batch_size)
            tf.add_to_collection('scores', rnn.scores)
            tf.add_to_collection('predictions', rnn.predictions)
            tf.add_to_collection('series_length', SERIES_LENGTH)

        def train_step(in_batch, target_batch):
            feed_dict = {
                rnn.input_vect: in_batch,
                rnn.target_vect: target_batch,
                rnn.dropout_keep_prob: 0.5,
                rnn.batch_size: len(in_batch),
                rnn.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([rnn.train_op, rnn.accuracy, rnn.loss, rnn.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                rnn.input_vect: in_batch,
                rnn.target_vect: target_batch,
                rnn.dropout_keep_prob: 1.0,
                rnn.batch_size: len(in_batch)
            }
            acc = session.run(rnn.accuracy, feed_dict)
            return acc

        train(training_step=train_step,
              preprocess=preprocess,
              num_batches=NUM_BATCHES,
              batch_size=BATCH_SIZE,
              collection_hook=collection_hook,
              logger=logger,
              name=TITLE,
              full=True,
              log_interval=50)

        validate(validation_step=val_step,
                 preprocess=preprocess,
                 batch_size=BATCH_SIZE,
                 logger=logger)


if __name__ == '__main__':
    main()