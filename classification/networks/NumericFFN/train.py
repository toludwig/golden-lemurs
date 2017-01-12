import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData, GloveWrapper
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .NumericFFN import NumericFFN
from .NumericFFN import repo_params
from .settings import *
import inspect
import os
import time

VAL_SIZE = 50
SAVE_INTERVAL = 20
NETWORK_PATH = 'classification/networks/NumericFFN/NumericFFN.py'
TITLE = 'FFN'
COMMENT = """neurons_hidden=%s
        num_batches=%d
        batch_size=%d
        learning rate=%f
""" % (NEURONS_HIDDEN, NUM_BATCHES, BATCH_SIZE, LEARNING_RATE)

CHECKPOINT_PATH = "out/FFN"
LOGGER = Logger(TITLE, COMMENT)


def test(ffn, model_path=CHECKPOINT_PATH):
    with tf.Session() as session:
        validation_data = TrainingData().validation(VAL_SIZE)

        tf.train.Saver().restore(session, model_path)
        results = []

        def val_step(in_batch, target_batch):
            feed_dict = {
                ffn.in_vector: in_batch,
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 1.0
            }
            acc = session.run(ffn.accuracy, feed_dict)
            return acc

        for batch in validation_data:
            input_vect = list(map(lambda x: repo_params(x), batch))
            target_vect = list(map(lambda x: int(x['Category']) - 1, batch))
            results.append(float(val_step(input_vect, target_vect)))

    LOGGER.set_test_acc(results)
    return np.average(results)


def train(ffn):
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
        tf.add_to_collection('score', ffn.scores)
        tf.add_to_collection('input', ffn.in_vector)
        tf.add_to_collection('dropout_keep_prop', ffn.dropout_keep_prob)
        tf.add_to_collection('predictions', ffn.predictions)
        tf.add_to_collection('category', ffn.category)

        def train_step(in_batch, target_batch, list_acc):
            feed_dict = {
                ffn.in_vector: in_batch,
                ffn.target_vect: target_batch,
                ffn.dropout_keep_prob: 0.5
            }
            _, new_acc, summary = session.run([ffn.train_op, ffn.accuracy, ffn.merged], feed_dict=feed_dict)

            list_acc.append(float(new_acc))
            summary_writer.add_summary(summary, i)

        acc = []

        for i in range(1, NUM_BATCHES + 1):
            batch = TrainingData().batch(BATCH_SIZE)
            input_vect = list(map(lambda x: repo_params(x), batch))
            output_vect = list(map(lambda x: int(x['Category']) - 1, batch))
            train_step(input_vect, output_vect, acc)
            print('Training step %d/%d: %f%% Accuracy' % (i, NUM_BATCHES, acc[-1] * 100))

            # Logging and backup
            if i % SAVE_INTERVAL == 0:
                LOGGER.set_training_acc(acc)
                if not os.path.exists(os.path.dirname(CHECKPOINT_PATH)):
                    os.makedirs(os.path.dirname(CHECKPOINT_PATH))

                checkpoint = saver.save(session, os.path.join(CHECKPOINT_PATH, TITLE), global_step=i)

        return checkpoint


def main():
    ffn = NumericFFN(parameters=len(FEATURES),
                     neurons_hidden=NEURONS_HIDDEN,
                     categories=6)
    checkpoint = train(ffn)
    result = test(ffn, checkpoint)
    LOGGER.set_score(result)
    print(result)

if __name__ == '__main__':
    main()
