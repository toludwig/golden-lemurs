#!/usr/bin/env python
import tensorflow as tf
from classification.Logger import Logger
from classification.networks.Ensemble import get_subnet_votes, rebuild_subnets
from classification.networks.NumericFFN import NumericFFN
from classification.Training import train, validate, TrainingData


TRAIN_ON_FULL_DATA = False


NEURONS_HIDDEN = [100, 100]
BATCH_SIZE = 300
NUM_BATCHES = 100
LEARNING_RATE = 1e-3
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

        train(training_step=train_step,
              preprocess=lambda x: x,
              num_batches=NUM_BATCHES,
              batch_size=BATCH_SIZE,
              collection_hook=collection_hook,
              logger=logger,
              name=TITLE,
              full=TRAIN_ON_FULL_DATA)

        if not TRAIN_ON_FULL_DATA:
            validate(validation_step=val_step,
                     preprocess=lambda x: x,
                     batch_size=BATCH_SIZE,
                     logger=logger)


if __name__ == '__main__':
    main()