#!/usr/bin/env python
import tensorflow as tf
from classification.Logger import Logger
from classification.Data import GloveWrapper
from classification.networks.TextCNN import TextCNN
from classification.Training import train, validate, TrainingData
import re


TRAIN_ON_FULL_DATA = False

SEQUENCE_LENGTH = 300
FILTER_SIZES = [2, 3, 4]
NUM_FILTERS = 120
BATCH_SIZE = 200
NUM_BATCHES = 200
LEARNING_RATE = 1e-3
NEURONS_HIDDEN = [100]
EMBEDDING_SIZE = 300
L2_REG = 0.01


TITLE = 'CNN-Files'
COMMENT = """neurons_hidden=%s
        num_batches=%d
        batch_size=%d
        learning rate=%f
""" % (NEURONS_HIDDEN, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE)


def preprocess(x, sequence_length=SEQUENCE_LENGTH):
    text = ""
    for i in x["Files"]:
        temp = re.sub('^.*/', '', i)
        text += ' ' + temp

    return GloveWrapper().tokenize(text, sequence_length)


def main():
    net = TextCNN(sequence_length=SEQUENCE_LENGTH,
                  num_classes=6,
                  filter_sizes=FILTER_SIZES,
                  num_filters=NUM_FILTERS,
                  neurons_hidden=NEURONS_HIDDEN,
                  learning_rate=LEARNING_RATE,
                  embedding_size=EMBEDDING_SIZE,
                  reg_lambda=L2_REG)

    logger = Logger(TITLE, COMMENT)
    logger.set_source(net)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('dropout_keep_prop', net.dropout_keep_prob)
            tf.add_to_collection('scores', net.scores)
            tf.add_to_collection('predictions', net.predictions)

        def train_step(in_batch, target_batch):
            feed_dict = {
                net.input_vect: in_batch,
                net.target_vect: target_batch,
                net.dropout_keep_prob: 0.5,
                net.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([net.train_op, net.accuracy, net.loss, net.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                net.input_vect: in_batch,
                net.target_vect: target_batch,
                net.dropout_keep_prob: 1.0
            }
            acc = session.run(net.accuracy, feed_dict)
            return acc

        train(training_step=train_step,
              preprocess=preprocess,
              num_batches=NUM_BATCHES,
              batch_size=BATCH_SIZE,
              collection_hook=collection_hook,
              logger=logger,
              name=TITLE,
              full=TRAIN_ON_FULL_DATA)

        if not TRAIN_ON_FULL_DATA:
            validate(validation_step=val_step,
                     preprocess=preprocess,
                     batch_size=BATCH_SIZE,
                     logger=logger)

if __name__ == '__main__':
    main()