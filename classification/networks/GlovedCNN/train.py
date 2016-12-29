import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN

BATCH_SIZE = 300
NUM_BATCHES = 100
LEARNING_RATE = 1e-3
VALIDATION_DATA = 300
VALIDATION_EPOCHES = 100
CHECKPOINT_PATH = "out/Gloved.ckpt"
TITLE = 'Muh net'
COMMENT = "preprocess, mid-deep, normal pooling, wide ffn"

def train(arg):
    with tf.Session() as session:
        saver = tf.train.Saver()
        data = TrainingData
        cnn = TextCNN(sequence_length=150,
                      num_classes=6,
                      filter_sizes[3, 4, 5],
                      num_filters=128)

        optimizer = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cnn.loss)

        sess.run(tf.initialize_all_variables())

        def train_step(in_batch, target_batch):
            feed_dict = {
                cnn.input = in_batch,
                cnn.target = target_batch,
                cnn.dropout_prob = 0.5
            }
            _, acc = sess.run([optimizer, cnn.accuracy], feed_dict)
            print(acc)

        for i in range(NUM_BATCHES):
            batch = data.batch(300)
            in = map(lambda x: x['Readme'], batch)
            out = map(lambda x: x['Category'], batch)
            train_step(in, out)
