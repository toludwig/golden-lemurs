#!/usr/bin/env python
import tensorflow as tf
from classification.Logger import Logger
from classification.Data import ExtensionVectorizer
from classification.networks.NumericFFN import NumericFFN
from classification.Training import train, validate, TrainingData


TRAIN_ON_FULL_DATA = False

NUM_EXTENSIONS = 300  # Number of extensions that we search the repository for. don't change
BATCH_SIZE = 200
NUM_BATCHES = 300
LEARNING_RATE = 1e-3
NEURONS_HIDDEN = [100, 100]  # Number of neurons in each hidden layer. layers are dynamically generated
L2_REG = 0.01  # L2 Regularization Lambda

TITLE = 'BoW'
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
    logger.set_source(net)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        # this is helpful should we later include this in an ensemble
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
              name=TITLE,
              full=TRAIN_ON_FULL_DATA)

        if not TRAIN_ON_FULL_DATA:
            validate(validation_step=val_step,
                     preprocess=vectorizer.vectorize,
                     batch_size=BATCH_SIZE,
                     logger=logger)

if __name__ == '__main__':
    main()