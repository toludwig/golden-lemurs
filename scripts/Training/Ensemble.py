#!/usr/bin/env python
import os
import sys

import tensorflow as tf

sys.path.insert(0, os.path.abspath('../..'))
from classification.Logger import Logger
from classification.networks.Ensemble import get_subnet_votes, rebuild_subnets
from classification.networks.NumericFFN import NumericFFN
from classification.Training import train, validate, TrainingData

NEURONS_HIDDEN = [100, 100]
BATCH_SIZE = 300
NUM_BATCHES = 100
LEARNING_RATE = 1e-3
SAVE_INTERVAL = 50
NUM_FEATURES = 12
L2_REG = 0.01

TITLE = 'Ensemble'
COMMENT = 'Placeholder'


def main():
    with tf.Session() as session:

        with tf.name_scope('Ensemble'):
            ffn = NumericFFN(NUM_FEATURES, NEURONS_HIDDEN, 6, LEARNING_RATE, L2_REG)

        session.run(tf.initialize_all_variables())
        rebuild_subnets()

        logger = Logger(TITLE, COMMENT)
        logger.set_source(ffn)

        def collection_hook():
            tf.add_to_collection('score', ffn.scores,)
            tf.add_to_collection('input', ffn.in_vector)
            tf.add_to_collection('dropout_keep_prop', ffn.dropout_keep_prob)
            tf.add_to_collection('predictions', ffn.predictions)
            tf.add_to_collection('category', ffn.category)

        def train_step(in_batch, target_batch):
            feed_dict = {
                ffn.in_vector: get_subnet_votes(in_batch),
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 0.5,
                ffn.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([ffn.train_op, ffn.accuracy, ffn.loss, ffn.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                ffn.in_vector: get_subnet_votes(in_batch),
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 1.0
            }
            acc = session.run(ffn.accuracy, feed_dict)
            return acc

        train(train_step, lambda x: x, NUM_BATCHES,
              BATCH_SIZE, collection_hook, logger,
              name=TITLE, full=True)

        validate(val_step, lambda x: x, BATCH_SIZE, logger)


if __name__ == '__main__':
    main()