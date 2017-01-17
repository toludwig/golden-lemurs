#!/usr/bin/env python
import tensorflow as tf
from classification.Logger import Logger
from classification.networks.NumericFFN import NumericFFN
from classification.Data import TrainingData
from classification.Training import train, validate

TRAIN_ON_FULL_DATA = True

NEURONS_HIDDEN = [100, 600]
BATCH_SIZE = 300
NUM_BATCHES = 400
LEARNING_RATE = 1e-3
GRADIENT_NORM = 5
L2_REG = 0.01

# What features of the repositories to feed into the network
FEATURES = ['Branches', 'Forks', 'NumberOfCommits', 'NumberOfContributors', 'Pulls', 'Stars', 'Subscribers']

TITLE = 'FFN'
COMMENT = """neurons_hidden=%s
        num_batches=%d
        batch_size=%d
        learning rate=%f
""" % (NEURONS_HIDDEN, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE)


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
    logger.set_source(ffn)

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

        train(training_step=train_step,
              preprocess=preprocess,
              num_batches=NUM_BATCHES,
              batch_size=BATCH_SIZE,
              collection_hook=collection_hook,
              logger=logger,
              name=TITLE,
              full=TRAIN_ON_FULL_DATA)

        if not TRAIN_ON_FULL_DATA:
            validate(
                validation_step=val_step,
                preprocess=preprocess,
                batch_size=BATCH_SIZE,
                logger=logger)


if __name__ == '__main__':
    main()
