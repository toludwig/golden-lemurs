import tensorflow as tf
import numpy as np
from ..Logger import Logger
from ..Data import TrainingData, GloveWrapper
from .. import TELEGRAM_API, TELEGRAM_TARGETS
from .TextCNN import TextCNN
import inspect

BATCH_SIZE = 300
NUM_BATCHES = 100
LEARNING_RATE = 1e-3
VAL_SIZE = 300
SAVE_INTERVAL = 20
CHECKPOINT_PATH = "out/Gloved.ckpt"
TITLE = 'Muh net'
COMMENT = "preprocess, mid-deep, normal pooling, wide ffn"

LOGGER = Logger(TITLE, COMMENT)


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

    LOGGER.set_test_acc(results)
    return np.average(results)


def train():
    with tf.Session() as session:
        data = TrainingData()
        glove = GloveWrapper()
        cnn = TextCNN(sequence_length=150,
                      num_classes=6,
                      filter_sizes=[3, 4, 5],
                      num_filters=128)

        #Logger.set_source(inspect.getsource(TextCNN))

        optimizer = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cnn.loss)

        session.run(tf.initialize_all_variables())
        saver = tf.train.Saver()

        def train_step(in_batch, target_batch, list_acc, list_cost):
            feed_dict = {
                cnn.input_vect: in_batch,
                cnn.target_vect: target_batch,
                cnn.dropout_keep_prob: 0.5
            }
            _, new_acc, new_cost = session.run([optimizer, cnn.accuracy, cnn.loss], feed_dict)
            list_acc.append(new_acc)
            list_cost.append(new_cost)
            print(acc)

        acc = []
        cost = []

        for i in range(NUM_BATCHES):
            batch = data.batch(BATCH_SIZE)
            input_vect = list(map(lambda x: glove.tokenize(x['Readme']), batch))
            output_vect = list(map(lambda x: x['Category'], batch))

            print(input_vect[0])
            train_step(input_vect, output_vect, acc, cost)

            # Logging and backup
            if i % SAVE_INTERVAL == 0:
                LOGGER.set_cost(cost)
                LOGGER.set_test_acc(acc)

                checkpoint = saver.save(session, CHECKPOINT_PATH, global_step=i)

            return checkpoint


def main():
    checkpoint = train()
    result = test(checkpoint)
    print(result)


if __name__ == '__main__':
    main()