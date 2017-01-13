import tensorflow as tf
from ..Logger import Logger
from ..Data import TrainingData, GloveWrapper
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN
from ..Training import train, validate

SEQUENCE_LENGTH = 200
FILTER_SIZES = [3, 4, 5, 6]
NUM_FILTERS = 164
BATCH_SIZE = 200
NUM_BATCHES = 350
LEARNING_RATE = 1e-3
NEURONS_HIDDEN = [100]
GRADIENT_NORM = 5

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


def main():
    cnn = TextCNN(sequence_length=SEQUENCE_LENGTH,
                  num_classes=6,
                  filter_sizes=FILTER_SIZES,
                  num_filters=NUM_FILTERS,
                  neurons_hidden=NEURONS_HIDDEN)

    logger = Logger(TITLE, COMMENT)
    logger.set_source(NETWORK_PATH)

    with tf.Session() as session:

        session.run(tf.initialize_all_variables())

        def collection_hook():
            tf.add_to_collection('features', cnn.h_pool_flat)
            tf.add_to_collection('input', cnn.input_vect)
            tf.add_to_collection('dropout_keep_prop', cnn.dropout_keep_prob)
            tf.add_to_collection('sequence_length', SEQUENCE_LENGTH)
            tf.add_to_collection('scores', cnn.scores)
            tf.add_to_collection('predictions', cnn.predictions)

        def train_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 0.5
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

        def preprocess(x):
            return GloveWrapper().tokenize(x['Readme'], SEQUENCE_LENGTH)

        train(train_step, preprocess, NUM_BATCHES,
              BATCH_SIZE, collection_hook, logger, CHECKPOINT_PATH)

        validate(val_step, preprocess, VAL_SIZE, logger)


if __name__ == '__main__':
    main()