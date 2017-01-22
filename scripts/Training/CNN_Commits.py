#!/usr/bin/env python
import tensorflow as tf
from classification.Logger import Logger
from classification.Data import Word2Wrap
from classification.networks.TextCNN import TextCNN
from classification.Training import train, validate, TrainingData


SEQUENCE_LENGTH = 400
FILTER_SIZES = [3, 4, 5]
NUM_FILTERS = 200
BATCH_SIZE = 200
NUM_BATCHES = 200
LEARNING_RATE = 1e-3
NEURONS_HIDDEN = [100]
L2_REG = 0.01
EMBEDDING_SIZE = 300

TITLE = 'Commits'
COMMENT = """sequence_length=%d
        filter_sizes=%s
        num_filters=%d
        num_batches=%d
        batch_size=%d
        learning rate=%f
        neurons_hidden=%s
""" % (SEQUENCE_LENGTH, FILTER_SIZES, NUM_FILTERS, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE, NEURONS_HIDDEN)


TRAIN_ON_FULL_DATA = True


def preprocess(x, sequence_length=SEQUENCE_LENGTH):
    commits = ""

    for i in x['CommitMessages']:
        commits += i
    return Word2Wrap().tokenize(commits, sequence_length)


def main():
    cnn = TextCNN(sequence_length=SEQUENCE_LENGTH,
                  num_classes=6,
                  filter_sizes=FILTER_SIZES,
                  num_filters=NUM_FILTERS,
                  neurons_hidden=NEURONS_HIDDEN,
                  learning_rate=LEARNING_RATE,
                  embedding_size=EMBEDDING_SIZE,
                  reg_lambda=L2_REG)

    logger = Logger(TITLE, COMMENT)
    logger.set_source(cnn)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('features', cnn.h_pool_flat)
            tf.add_to_collection('input', cnn.input_vect)
            tf.add_to_collection('dropout_keep_prop', cnn.dropout_keep_prob)
            tf.add_to_collection('sequence_length_commits', SEQUENCE_LENGTH)
            tf.add_to_collection('scores', cnn.scores)
            tf.add_to_collection('predictions', cnn.predictions)

        def train_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 0.5,
                cnn.class_weights: TrainingData().factors
            }
            _, acc, cost, summary = session.run([cnn.train_op, cnn.accuracy, cnn.loss, cnn.merged],
                                                feed_dict=feed_dict)
            return acc, cost, summary

        def val_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 1.0
            }
            acc = session.run(cnn.accuracy, feed_dict)
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