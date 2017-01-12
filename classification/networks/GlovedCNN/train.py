import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData, GloveWrapper
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN
from .settings import *
import inspect
import os
import time

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

LOGGER = Logger(TITLE, COMMENT)


def test(cnn, model_path=CHECKPOINT_PATH):
    with tf.Session() as session:
        validation_data = TrainingData().validation(VAL_SIZE)

        tf.train.Saver().restore(session, model_path)
        results = []

        def val_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 1.0
            }
            acc = session.run(cnn.accuracy, feed_dict)
            return acc

        for batch in validation_data:
            input_vect = list(map(lambda x: GloveWrapper().tokenize(x['Readme'], SEQUENCE_LENGTH), batch))
            target_vect = list(map(lambda x: int(x['Category']) - 1, batch))
            results.append(float(val_step(input_vect, target_vect)))

    LOGGER.set_test_acc(results)
    return np.average(results)


def train(cnn):
    with tf.Session() as session:

        LOGGER.set_source(NETWORK_PATH)

        now = time.strftime("%c")
        sum_dir = os.path.join(CHECKPOINT_PATH, 'summary', now)
        save_dir = os.path.join(CHECKPOINT_PATH, now)
        for directory in [sum_dir, save_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        summary_writer = tf.summary.FileWriter(sum_dir, session.graph)
        session.run(tf.initialize_all_variables())

        saver = tf.train.Saver()

        tf.add_to_collection('features', cnn.h_pool_flat)
        tf.add_to_collection('input', cnn.input_vect)
        tf.add_to_collection('dropout_keep_prop', cnn.dropout_keep_prob)
        tf.add_to_collection('sequence_length', SEQUENCE_LENGTH)
        tf.add_to_collection('scores', cnn.scores)
        tf.add_to_collection('predictions', cnn.predictions)

        def train_step(in_batch, target_batch, list_acc):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 0.5
            }
            _, new_acc, pred, summary = session.run([cnn.train_op, cnn.accuracy, cnn.predictions, cnn.merged],
                                                    feed_dict=feed_dict)
            list_acc.append(float(new_acc))
            summary_writer.add_summary(summary, i)

        acc = []

        for i in range(1, NUM_BATCHES + 1):
            batch = TrainingData().batch(BATCH_SIZE)
            input_vect = list(map(lambda x: GloveWrapper().tokenize(x['Readme'], SEQUENCE_LENGTH), batch))
            output_vect = list(map(lambda x: int(x['Category']) - 1, batch))
            train_step(input_vect, output_vect, acc)
            print('Training step %d/%d: %f%% Accuracy' % (i, NUM_BATCHES, acc[-1] * 100))

            # Logging and backup
            if i % SAVE_INTERVAL == 0:
                LOGGER.set_training_acc(acc)
                if not os.path.exists(os.path.dirname(CHECKPOINT_PATH)):
                    os.makedirs(os.path.dirname(CHECKPOINT_PATH))

                checkpoint = saver.save(session, os.path.join(save_dir, TITLE), global_step=i)

        return checkpoint


def main():
    cnn = TextCNN(sequence_length=SEQUENCE_LENGTH,
                  num_classes=6,
                  filter_sizes=FILTER_SIZES,
                  num_filters=NUM_FILTERS,
                  neurons_hidden=NEURONS_HIDDEN)
    checkpoint = train(cnn)
    result = test(cnn, checkpoint)
    LOGGER.set_score(result)
    print(result)


if __name__ == '__main__':
    main()