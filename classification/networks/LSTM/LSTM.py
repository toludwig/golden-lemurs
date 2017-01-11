import tensorflow as tf
from .settings import LEARNING_RATE, GRADIENT_NORM

class LSTM:

    def __init__(self,
                 num_layers,
                 hidden_size,
                 num_classes,
                 series_length,
                 neurons_hidden):

        self.input_vect = tf.placeholder(tf.float32, [None, series_length], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='labels')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.batch_size = tf.placeholder(tf.int32, name='batch_size')

        input_list = tf.unstack(tf.expand_dims(self.input_vect, axis=2), axis=1)

        # LSTM Layers
        with tf.name_scope('LSTM'):
            cell = tf.nn.rnn_cell.LSTMCell(hidden_size)
            multi_cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_layers)
            state = multi_cell.zero_state(self.batch_size, tf.float32)
            self.lstm, state = multi_cell(self.input_vect, state)

        # Hidden Layers
        self.hidden_layers = []
        for i, num_neurons in enumerate(neurons_hidden):
            with tf.name_scope('fully_connected-%d' % num_neurons):
                w = tf.Variable(tf.truncated_normal([hidden_size if i == 0 else neurons_hidden[i - 1],
                                                     neurons_hidden[i]], stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[neurons_hidden[i]]), name="b")
                self.hidden_layers.append(tf.nn.relu(tf.nn.xw_plus_b(
                    self.lstm if i == 0 else self.hidden_layers[-1], w, b, name="ffn")))

        with tf.name_scope('dropout'):
            self.drop = tf.nn.dropout(self.hidden_layers[-1], self.dropout_keep_prob)

        # Output Layer
        with tf.name_scope("output"):
            w = tf.Variable(tf.truncated_normal([neurons_hidden[-1], num_classes], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.drop, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores)

        # CalculateMean cross-entropy loss
        with tf.name_scope('loss'):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            self.loss = tf.reduce_sum(losses) / tf.cast(self.batch_size, tf.float32)

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")

        # Adam Optimizer with exponential decay
        with tf.name_scope("Optimizer"):
            step = tf.Variable(0, trainable=False)
            rate = tf.train.exponential_decay(LEARNING_RATE, step, 1, 0.9999)
            optimizer = tf.train.AdamOptimizer(rate)
            self.train_op = optimizer.minimize(self.loss, global_step=step)

