import tensorflow as tf
from .settings import LEARNING_RATE

from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops

class LSTM:

    def __init__(self,
                 num_layers,
                 hidden_size,
                 num_classes,
                 series_length,
                 gradient_limit=5):

        self.input_vect = tf.placeholder(tf.float32, [None, series_length], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='labels')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.batch_size = tf.placeholder(tf.int32, name='batch_size')

        # LSTM Layers
        with tf.name_scope('LSTM'):
            cell = tf.nn.rnn_cell.LSTMCell(hidden_size)
            cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=self.dropout_keep_prob)
            multi_cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_layers)
            state = multi_cell.zero_state(self.batch_size, tf.float32)
            self.lstm, state = multi_cell(self.input_vect, state)

        # Output Layer
        with tf.name_scope("output"):
            w = tf.Variable(tf.truncated_normal([hidden_size, num_classes], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.lstm, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores)

        # CalculateMean cross-entropy loss
        with tf.name_scope('loss'):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            self.loss = tf.reduce_sum(losses) / tf.cast(self.batch_size, tf.float32)
            tf.summary.scalar('loss', self.loss)

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")
            tf.summary.scalar('accuracy', self.accuracy)

        # Adam Optimizer with exponential decay and gradient clipping
        with tf.name_scope("Optimizer"):
            step = tf.Variable(0, trainable=False)
            rate = tf.train.exponential_decay(LEARNING_RATE, step, 1, 0.9999)
            optimizer = tf.train.AdamOptimizer(rate)
            variables = tf.trainable_variables()
            gradients = tf.gradients(self.loss, variables)
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, gradient_limit)
            gradients = zip(clipped_gradients, variables)
            self.train_op = optimizer.apply_gradients(gradients, global_step=step)

            # Keep track of gradient values and sparsity
        gradient_summaries = []
        for gradient, variable in gradients:
            if g is not None:
                grad_hist_summary = tf.histogram_summary("{}/grad/hist".format(variable.name), gradient)
                sparsity_summary = tf.scalar_summary("{}/grad/sparsity".format(variable.name), tf.nn.zero_fraction(gradient))
                gradient_summaries.append(grad_hist_summary)
                gradient_summaries.append(sparsity_summary)
        self.grad_summaries_merged = tf.merge_summary(gradient_summaries)

        self.merged = tf.summary.merge_all()

