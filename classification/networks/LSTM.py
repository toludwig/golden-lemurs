import tensorflow as tf
from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops


class LSTM:
    """
    Long Short Term Memory Network for time series classification. In this case we used the summed up months of
    a repositories as our input sequence. We traverse this sequence with an bidirectional lstm (meaning one lstm cell
    moving past->future and one moving future->past).
    We hoped that the workflow of the group working on the repository would be reflected in this feature, which could result
    in quite a strong classifier.
    """

    def __init__(self,
                 hidden_size,
                 num_classes,
                 series_length,
                 learning_rate):
        """
        :param hidden_size: Number of hidden units in the lstm cells
        :param num_classes: Number of classes in the output layer
        :param series_length: Number of bins in the time series
        :param learning_rate: learning rate
        """

        self.input_vect = tf.placeholder(tf.float32, [None, series_length], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='labels')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.batch_size = tf.placeholder(tf.int32, name='batch_size')
        self.class_weights = tf.placeholder(tf.float32, [num_classes], name='class_weights')

        # transform data into format needed by tensorflow rnns
        sequence = tf.unstack(tf.expand_dims(self.input_vect, axis=2), axis=1)

        # LSTM Layers
        with tf.name_scope('LSTM'):
            # We use a bidirectional LSTM net
            forward_cell = tf.nn.rnn_cell.LSTMCell(hidden_size, initializer=tf.contrib.layers.xavier_initializer())
            backward_cell = tf.nn.rnn_cell.LSTMCell(hidden_size, initializer=tf.contrib.layers.xavier_initializer())
            """
            No need for regularization here as the LSTMs inner architecture prevents gradient vanishing. exploding
            gradients are dealt with by gradient clipping.
            """

            self.lstm, _, _ = tf.nn.bidirectional_rnn(forward_cell, backward_cell, sequence, dtype=tf.float32)  # Non stateful

        # Output Layer
        with tf.name_scope("output"):
            w = tf.get_variable('W', shape=[hidden_size * 2, num_classes],
                                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.lstm[-1], w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores, name='predictions')

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            scale = tf.gather(self.class_weights, self.target_vect)
            self.loss = tf.reduce_mean(losses * scale) / tf.cast(self.batch_size, tf.float32)
            tf.summary.scalar('loss', self.loss)

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")
            tf.summary.scalar('accuracy', self.accuracy)

        # Adam Optimizer with exponential decay and gradient clipping
        with tf.name_scope("Optimizer"):
            step = tf.Variable(0, trainable=False)
            rate = tf.train.exponential_decay(learning_rate, step, 1, 0.9999)
            optimizer = tf.train.AdamOptimizer(rate)
            tvars = tf.trainable_variables()
            gradients = tf.gradients(self.loss, tvars)
            clipped_gradients,_ = tf.clip_by_global_norm(gradients, 5)
            self.train_op = optimizer.apply_gradients(zip(clipped_gradients, tvars), global_step=step)

        # Keep track of gradient values and sparsity
        for gradient, variable in zip(clipped_gradients, tvars):
            if isinstance(gradient, ops.IndexedSlices):
                grad_values = gradient.values
            else:
                grad_values = gradient
            tf.summary.histogram(variable.name, variable)
            tf.summary.histogram(variable.name + "/gradients", grad_values)
            tf.summary.histogram(variable.name + "/gradient_norm", clip_ops.global_norm([grad_values]))
            tf.summary.scalar(variable.name + "/grad/sparsity", tf.nn.zero_fraction(gradient))

        self.merged = tf.summary.merge_all()

