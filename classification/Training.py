"""
Provides a general interface for Training and Validating Networks
"""

import os
from os.path import join
import time

import numpy as np
import tensorflow as tf

from classification.Data import TrainingData
from classification import MODEL_DIR, OUT_DIR


def train(training_step,
          preprocess,
          num_batches,
          batch_size,
          collection_hook,
          logger,
          name,
          full=False,
          log_interval=20):
    """
    This trains a network with our repository dataset. Has to be called within a tf.Session
    :param training_step the function used for the training step.
           Has to return a triple (accuracy, loss, merged_summary)
    :param preprocess preprocessing lambda to run on the data
    :param num_batches number of batches to use
    :param batch_size size of batches to use
    :param collection_hook the function to call for session collection setup
    :param logger a mongodb logger to use
    :param checkpoit_path directory to use for checkpoints and tensorboard logs
    :param log_interval logging interval in batches
    :return the path to the latest checkpoint.
    """

    print("Started Training...")

    checkpoint_path = join(OUT_DIR, name)

    now = time.strftime("%c")
    sum_dir = os.path.join(checkpoint_path, 'summary', now)
    save_dir = os.path.join(checkpoint_path, now)

    # Create repositories
    for directory in [sum_dir, save_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    session = tf.get_default_session()

    summary_writer = tf.summary.FileWriter(sum_dir, session.graph)

    saver = tf.train.Saver()

    # Add variables to collection for later restoration during evaluation
    collection_hook()

    acc = []
    loss = []

    if full:
        data = [[TrainingData().full(batch_size)] for i in range(num_batches)]
    else:
        data = [[TrainingData().batch(batch_size)] for i in range(num_batches)]

    for i, batch in enumerate(data):
        i += 1
        batch = TrainingData().batch(batch_size)
        input_vect = list(map(lambda x: preprocess(x), batch))
        output_vect = list(map(lambda x: int(x['Category']) - 1, batch))
        new_acc, new_loss, summary = training_step(input_vect, output_vect)

        acc.append(float(new_acc))
        loss.append(float(new_loss))
        summary_writer.add_summary(summary, i)

        print('Training step %d/%d: %f%% Accuracy' % (i, num_batches, acc[-1] * 100))

        # Logging and backup
        if i % log_interval == 0 and not full:

            checkpoint = saver.save(session, os.path.join(save_dir, name), global_step=i)

        logger.set_training_acc(acc)
        logger.set_cost(loss)

    print("Training finished")
    if full:
        checkpoint = saver.save(session, os.path.join(MODEL_DIR, name))

    return checkpoint


def validate(validation_step,
             preprocess,
             batch_size,
             logger):
    """
    This trains a network with our repository dataset. Has to be called within a tf.Session
    :param validation_step the function used for the validation step.
    :param preprocess preprocessing lambda to run on the data
    :param batch_size size of batches to use
    :param logger a mongodb logger to use
    :return the path to the latest checkpoint.
    """
    print("Starting Validation...")

    validation_data = TrainingData().validation(batch_size)

    acc = []

    for batch in validation_data:
        input_vect = list(map(lambda x: preprocess(x), batch))
        output_vect = list(map(lambda x: int(x['Category']) - 1, batch))
        new_acc = validation_step(input_vect, output_vect)

        acc.append(float(new_acc))

    score = np.average(acc)

    logger.set_test_acc(acc)
    logger.set_score(score)

    print("Validation finished. Accuracy was %f%%" % (score * 100))

    return score
