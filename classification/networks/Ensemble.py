from .Logger import Logger
from .NumericFFN.NumericFFN import NumericFFN, repo_params
import tensorflow as tf
import numpy as np
import os
from .Data import GloveWrapper, TrainingData, commit_time_profile


CNN_DATA = 'out/CNN/TextCNN-340'
CNN_META = 'out/CNN/TextCNN-340.meta'

RNN_DATA = 'out/RNN/RNN-300'
RNN_META = 'out/RNN/RNN-300.meta'

FNN_DATA = 'out/FFN/FNN-400'
FNN_META = 'out/FFN/FNN-400.meta'

NEURONS_HIDDEN = [100, 100]
BATCH_SIZE = 350
NUM_BATCHES = 200
LEARNING_RATE = 1e-3
SAVE_INTERVAL = 50
NUM_FEATURES = 18

CHECKPOINT_PATH = "out/Ensemble"
TITLE = 'My Poor GPU'
DESCRIPTION = 'Placeholder'
LOGGER = Logger(TITLE, DESCRIPTION)


def rebuild_subnets(session):
    """
    loads the pretrained CNN and RNN for evaluation. Must be given a tf.Session to restore to
    """
    saver = tf.train.import_meta_graph(CNN_META, import_scope='CNN')
    saver.restore(session, CNN_DATA)

    saver = tf.train.import_meta_graph(RNN_META, import_scope='RNN')
    saver.restore(session, RNN_DATA)

    saver = tf.train.import_meta_graph(FNN_META, import_scope='FFN')
    saver.restore(session, FNN_DATA)


def get_subnet_features(batch, session):
    """
    Evaluates the input on the subnets and returns features for further classification.
    in_batch has to be a list.
    rebuild_subnets must have had been called on session beforehand
    """

    def cnn_eval(batch):
        input = tf.get_collection('input', scope='CNN')[0]
        features = tf.get_collection('features', scope='CNN')[0]
        dropout = tf.get_collection("dropout_keep_prop", scope='CNN')[0]
        scores = tf.get_collection("scores", scope='CNN')[0]
        sequence_length = tf.get_collection('sequence_length')[0]

        feed_dict = {
            input: list(map(lambda x: GloveWrapper().tokenize(x['Readme'], sequence_length), batch)),
            dropout: 1
        }
        return session.run(scores, feed_dict)

    def rnn_eval(batch):
        input = tf.get_collection('input', scope='RNN')[0]
        features = tf.get_collection('features', scope='RNN')[0]
        dropout = tf.get_collection("dropout_keep_prop", scope='RNN')[0]
        sequence_length = tf.get_collection('series_length')[0]
        batch_size = tf.get_collection('batch_size')[0]
        scores = tf.get_collection("scores", scope='RNN')[0]

        feed_dict = {
            input: list(map(lambda x: commit_time_profile(x['CommitTimes']), batch)),
            dropout: 1,
            batch_size: len(batch)
        }
        return session.run(scores, feed_dict)

    def fnn_eval(batch):
        input = tf.get_collection('input', scope='FFN')[0]
        dropout = tf.get_collection("dropout_keep_prop", scope='FFN')[0]
        prediction = tf.get_collection('predictions', scope='FFN')[0]
        scores = tf.get_collection("score", scope='FFN')[0]

        feed_dict = {
            input: list(map(lambda x: repo_params(x), batch)),
            dropout: 1,
        }
        return session.run(prediction, feed_dict)

    # This just evaluates the input on both networks and concatenates the features extracted
    return np.column_stack((np.column_stack((cnn_eval(batch), rnn_eval(batch))), fnn_eval(batch)))


def train(ffn, session):

    saver = tf.train.Saver()
    tf.add_to_collection('score', ffn.scores)
    tf.add_to_collection('input', ffn.in_vector)
    tf.add_to_collection('dropout_keep_prop', ffn.dropout_keep_prob)

    def train_step(in_batch, target_batch, list_acc):
        feed_dict = {
            ffn.in_vector: in_batch,
            ffn.target_vect: target_batch,
            ffn.dropout_keep_prob: 1
        }
        _, new_acc, pred = session.run([ffn.train_op, ffn.accuracy, ffn.predictions], feed_dict=feed_dict)
        print(pred)
        list_acc.append(float(new_acc))

    acc = []

    for i in range(1, NUM_BATCHES + 1):
        batch = TrainingData().batch(BATCH_SIZE)


        # Get additional features for regression
        input_vect = get_subnet_features(batch, session)
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
    with tf.Session() as session:
        ffn = NumericFFN(NUM_FEATURES, NEURONS_HIDDEN, 6)

        session.run(tf.initialize_all_variables())
        rebuild_subnets(session)

        train(ffn, session)

if __name__ == '__main__':
    main()
