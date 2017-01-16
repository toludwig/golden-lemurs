"""
Network that uses two C-LSTM networks as its input. One trained on Readmes and the other on the CommitMessages.
The performance is superior to the performance of the individual nets.
Formally this is a special case of Ensemble Averaging, where we use a nonlinear classifier instead of simply averaging.
"""

import numpy as np
import tensorflow as tf

from classification.Data import GloveWrapper, TrainingData
from classification.Logger import Logger
from classification.Training import train, validate
from classification.networks.NumericFFN import NumericFFN
from os.path import join
from .. import MODEL_DIR


NET_README_PATH = join(MODEL_DIR, 'C-LSTM-Readme')
NET_COMMITS_PATH = join(MODEL_DIR, 'C-LSTM-Commits')

ENSEMBLE_PATH = join(MODEL_DIR, 'Ensemble')


def rebuild_subnets():
    """
    loads the pretrained CNN and RNN for evaluation. Must be given a tf.Session to restore to.
    All nets used by subnet eval must be restored here.
    """

    session = tf.get_default_session()

    tf.train.import_meta_graph(NET_README_PATH + '.meta', import_scope='Readme').restore(session, NET_README_PATH)
    tf.train.import_meta_graph(NET_COMMITS_PATH + '.meta', import_scope='Commits').restore(session, NET_COMMITS_PATH)


def rebuild_full():
    """
    Loads all Subnets and the Ensemble into the current tf.Session
    """
    session = tf.get_default_session()
    tf.train.import_meta_graph(ENSEMBLE_PATH + '.meta').restore(session, ENSEMBLE_PATH)
    GloveWrapper()


def ensemble_eval(repos):
    session = tf.get_default_session()
    in_vect = get_subnet_votes(repos)
    # These give variables or tensors explicitly stored in the models. refer to the train files for the names.
    input = tf.get_collection('input', scope='Ensemble')[0]
    predictions = tf.get_collection('predictions', scope='Ensemble')[0]
    dropout = tf.get_collection("dropout_keep_prop", scope='Ensemble')[0]

    feed_dict = {
        input: in_vect,
        dropout: 1
    }

    return session.run(predictions, feed_dict)


def get_subnet_votes(batch):
    """
    Evaluates the input on the subnets and returns features for further classification.
    in_batch has to be a list.
    rebuild_subnets must have had been called on session beforehand
    """

    session = tf.get_default_session()

    def readme_eval(batch):

        # Get all variables/Tensors needed for operation
        input = tf.get_collection('input', scope='Readme')[0]
        features = tf.get_collection('features', scope='Readme')[0]
        dropout = tf.get_collection("dropout_keep_prop", scope='Readme')[0]
        scores = tf.get_collection("scores", scope='Readme')[0]
        sequence_length = tf.get_collection('sequence_length', scope="Readme")[0]
        predictions = tf.get_collection('predictions', scope='Readme')[0]

        def preprocess(x, sequence_length):
            return GloveWrapper().tokenize(x['Readme'], sequence_length)

        feed_dict = {
            input: list(map(lambda x: preprocess(x, sequence_length), batch)),
            dropout: 1
        }
        return session.run(predictions, feed_dict)

    def commits_eval(batch):
        input = tf.get_collection('input', scope='Commits')[0]
        features = tf.get_collection('features', scope='Commits')[0]
        dropout = tf.get_collection("dropout_keep_prop", scope='Commits')[0]
        scores = tf.get_collection("scores", scope='Commits')[0]
        sequence_length = tf.get_collection('sequence_length', scope='Commits')[0]
        predictions = tf.get_collection('predictions', scope='Commits')[0]

        def preprocess(x, sequence_length):
            commits = ""

            for i in x['CommitMessages']:
                commits += i
            return GloveWrapper().tokenize(commits, sequence_length)

        feed_dict = {
            input: list(map(lambda x: preprocess(x, sequence_length), batch)),
            dropout: 1
        }
        return session.run(predictions, feed_dict)

    # This just evaluates the input on both networks and concatenates the features extracted
    return np.column_stack((commits_eval(batch), readme_eval(batch)))

