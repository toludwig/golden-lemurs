import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN

BATCH_SIZE = 300
NUM_BATCHES = 100
LEARNING_RATE = 1e-3
VAL_SIZE = 300
CHECKPOINT_PATH = "out/Gloved.ckpt"
TITLE = 'Muh net'
COMMENT = "preprocess, mid-deep, normal pooling, wide ffn"


def test(model_path=CHECKPOINT_PATH):
    with tf.Session() as session:
        tf.train.Saver().restore(session, model_path)
        validation_data = TrainingData().validation(VAL_SIZE)
        cnn = TextCNN(sequence_length=150,
                      num_classes=6,
                      filter_sizes=[3, 4, 5],
                      num_filters=128)
        results = []

        def val_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 1.0
            }
            acc = session.run([cnn.accuracy], feed_dict)
            return acc

        for batch in validation_data:
            input_vect = map(lambda x: x['Readme'], batch)
            target_vect = map(lambda x: x['Category'], batch)
            results.append(val_step(input_vect, target_vect))
    return np.average(results)


def train():
    with tf.Session() as session:
        saver = tf.train.Saver()
        data = TrainingData()
        cnn = TextCNN(sequence_length=150,
                      num_classes=6,
                      filter_sizes=[3, 4, 5],
                      num_filters=128)

        optimizer = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cnn.loss)

        session.run(tf.initialize_all_variables())

        def train_step(in_batch, target_batch):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 0.5
            }
            _, acc = session.run([optimizer, cnn.accuracy], feed_dict)
            print(acc)

        for i in range(NUM_BATCHES):
            batch = data.batch(BATCH_SIZE)
            input_vect = map(lambda x: x['Readme'], batch)
            output_vect = map(lambda x: x['Category'], batch)
            train_step(input_vect, output_vect)
