from .Logger import Logger
from .NumericFFN.NumericFFN import NumericFFN
from .Training import train, validate
import tensorflow as tf
import numpy as np
from .Data import GloveWrapper, TrainingData, commit_time_profile
from .NumericFFN.train import preprocess as repo_params
from .NumericFFN.train import NETWORK_PATH


CNN_DATA = 'out/CNN/TextCNN-340'
CNN_META = 'out/CNN/TextCNN-340.meta'

RNN_DATA = 'out/RNN/RNN-400'
RNN_META = 'out/RNN/RNN-400.meta'

FNN_DATA = 'out/FFN/FNN-400'
FNN_META = 'out/FFN/FNN-400.meta'

ENSEMBLE_DATA = 'out/Ensemble/'
ENSEMBLE_META = 'out/Ensemble/'

NEURONS_HIDDEN = [100, 100]
BATCH_SIZE = 350
NUM_BATCHES = 200
LEARNING_RATE = 1e-3
SAVE_INTERVAL = 50
NUM_FEATURES = 18

CHECKPOINT_PATH = "out/Ensemble"
TITLE = 'Ensemble'
COMMENT = 'Placeholder'


def rebuild_subnets():
    """
    loads the pretrained CNN and RNN for evaluation. Must be given a tf.Session to restore to
    """

    session = tf.get_default_session()

    tf.train.import_meta_graph(CNN_META, import_scope='CNN').restore(session, CNN_DATA)
    tf.train.import_meta_graph(RNN_META, import_scope='RNN').restore(session, RNN_DATA)
    tf.train.import_meta_graph(FNN_META, import_scope='FFN').restore(session, FNN_DATA)


def rebuild_full():
    session = tf.get_default_session()

    rebuild_subnets()
    tf.train.import_meta_graph(ENSEMBLE_META, import_scope='Ensemble').restore(session, ENSEMBLE_DATA)


def ensemble_eval(repos):
    session = tf.get_default_session()
    in_vect = get_subnet_features(repos)
    # These give me variables or tensors I explicitly stored in the models. refer to the train files for the names.
    input = tf.get_collection('input', scope='Ensemble')[0]
    predictions = tf.get_collection('category', scope='Ensemble')[0]
    dropout = tf.get_collection("dropout_keep_prop", scope='Ensemble')[0]

    feed_dict = {
        input: in_vect,
        dropout: 1
    }

    return session.run(predictions, feed_dict)


def get_subnet_features(batch):
    """
    Evaluates the input on the subnets and returns features for further classification.
    in_batch has to be a list.
    rebuild_subnets must have had been called on session beforehand
    """

    session = tf.get_default_session()

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


def main():
    with tf.Session() as session:
        ffn = NumericFFN(NUM_FEATURES, NEURONS_HIDDEN, 6)

        session.run(tf.initialize_all_variables())
        rebuild_subnets()

        logger = Logger(TITLE, COMMENT)
        logger.set_source(NETWORK_PATH)

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
                ffn.dropout_keep_prob: 0.5
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

        train(train_step, get_subnet_features, NUM_BATCHES,
              BATCH_SIZE, collection_hook, logger, CHECKPOINT_PATH)

        validate(val_step, get_subnet_features, BATCH_SIZE, logger)


if __name__ == '__main__':
    main()
