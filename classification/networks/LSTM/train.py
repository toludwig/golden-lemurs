import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData, commit_time_profile
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .LSTM import LSTM
from .settings import *
import inspect
import os
import numpy as np

SAVE_INTERVAL = 20
CHECKPOINT_PATH = "out/RNN"
NETWORK_PATH = 'classification/networks/LSTM/LSTM.py'
TITLE = 'RNN'
COMMENT = """neurons_fully=%s
             learning_rate=%f
             num_layers=%d
             num_batches=%d
             batch_size=%d
             gradient_norm=%d
             series_length=%d
             neurons_hidden=%d
""" % (NEURONS_FULL, LEARNING_RATE, NUM_LAYERS, NUM_BATCHES, BATCH_SIZE, GRADIENT_NORM, SERIES_LENGTH, NEURONS_HIDDEN)

LOGGER = Logger(TITLE, COMMENT)


def test(rnn, model_path=CHECKPOINT_PATH):
    with tf.Session() as session:
        validation_data = TrainingData().validation(BATCH_SIZE)

        tf.train.Saver().restore(session, model_path)
        results = []

        def val_step(in_batch, target_batch):
            feed_dict = {
                rnn.input_vect: in_batch,
                rnn.target_vect: target_batch,
                rnn.dropout_keep_prob: 1.0,
                rnn.batch_size: len(in_batch)
            }
            acc = session.run(rnn.accuracy, feed_dict)
            return acc

        for batch in validation_data:
            input_vect = list(map(lambda x: commit_time_profile(x['CommitTimes']), batch))
            target_vect = list(map(lambda x: int(x['Category']) - 1, batch))
            results.append(float(val_step(input_vect, target_vect)))

    LOGGER.set_test_acc(results)
    return np.average(results)


def train(rnn):
    with tf.Session() as session:

        LOGGER.set_source(NETWORK_PATH)

        session.run(tf.initialize_all_variables())
        saver = tf.train.Saver()
        tf.add_to_collection('features', rnn.lstm)
        tf.add_to_collection('input', rnn.input_vect)
        tf.add_to_collection('dropout_keep_prop', rnn.dropout_keep_prob)
        tf.add_to_collection('batch_size', rnn.batch_size)
        tf.add_to_collection('scores', rnn.scores)
        tf.add_to_collection('predictions', rnn.predictions)
        tf.add_to_collection('series_length', SERIES_LENGTH)


        def train_step(in_batch, target_batch, list_acc):
            feed_dict = {
                rnn.input_vect: in_batch,
                rnn.target_vect: target_batch,
                rnn.dropout_keep_prob: 0.5,
                rnn.batch_size: len(in_batch)
            }
            _, new_acc = session.run([rnn.train_op, rnn.accuracy], feed_dict=feed_dict)
            list_acc.append(float(new_acc))

        acc = []

        for i in range(1, NUM_BATCHES + 1):
            batch = TrainingData().batch(BATCH_SIZE)
            input_vect = list(map(lambda x: commit_time_profile(x['CommitTimes']), batch))
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
    rnn = LSTM(NUM_LAYERS, NEURONS_HIDDEN, 6, SERIES_LENGTH, NEURONS_FULL)
    checkpoint = train(rnn)
    result = test(rnn, checkpoint)
    LOGGER.set_score(result)
    print(result)


if __name__ == '__main__':
    main()