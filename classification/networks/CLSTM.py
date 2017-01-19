import tensorflow as tf

from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops
from tensorflow.contrib.layers import l2_regularizer

class CLSTM:
    """
    Network consisting of an CNN and an LSTM for text classification. The LSTM uses features extracted by the CNN in order
    to perform text classification. This achieves better performance then an CNN on its own because the LSTM is able to learn
    global semantics in addition to the local features extracted by the CNN. Orginal description of this architecture can
    be found in Chunting Zhou, Chonglin Sun, Zhiyuan Liu: “A C-LSTM Neural Network for Text Classification”,
    2015; [http://arxiv.org/abs/1511.08630 arXiv:1511.08630].
    We sadly were not able to reproduce a similiar performance gain compared to a CNN as described in the paper.
    This could be caused by the fact that this network is best suited for finding the global semantic of a text, which
    is not quite what is needed in this task. A pure CNN based approach acts like a sort of improved bag-of-words
    which filters for certain local features of the sort 'this dataset'. This might be more powerful here than a better
    semantic understanding.
    """

    def __init__(self,
                 sequence_length,
                 num_classes,
                 filter_size,
                 num_filters,
                 learning_rate,
                 embedding_size,
                 reg_lambda,
                 lstm_size):

        self.input_vect = tf.placeholder(tf.float32, [None, sequence_length, embedding_size], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='target')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.class_weights = tf.placeholder(tf.float32, [num_classes], name='class_weights')
        self.batch_size = tf.placeholder(tf.int32, name='batch_size')

        self.weights = []

        input = tf.nn.dropout(self.input_vect, self.dropout_keep_prob)

        with tf.name_scope("embedding"):
            self.embedded_chars_expanded = tf.expand_dims(self.input_vect, -1)

        # Convolution and max-pooling Layer
        with tf.variable_scope("convolution"):

            # Convolution Layer
            filter_shape = [filter_size, embedding_size, num_filters]
            w = tf.get_variable("W", shape=filter_shape,
                                initializer=tf.contrib.layers.xavier_initializer_conv2d())

            b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")

            conv = tf.nn.conv1d(
                input,
                w,  # Uses the kernel widths defined in filter sizes
                stride=1,
                padding="VALID",
                name="conv")

            # Apply relu
            features = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")

        # LSTM Layers
        with tf.name_scope('LSTM'):
            sequence = tf.unstack(features, axis=1)
            cell = tf.nn.rnn_cell.LSTMCell(lstm_size,
                                           initializer=tf.contrib.layers.xavier_initializer())
            """
            No need for regularization here as the LSTMs inner architecture prevents gradient vanishing. exploding
            gradients are dealt with by gradient clipping.
            """
            self.lstm, _ = tf.nn.rnn(cell, sequence, dtype=tf.float32)

        drop = tf.nn.dropout(self.lstm[-1], self.dropout_keep_prob)

        with tf.variable_scope("output"):
            w = tf.get_variable('W',
                                shape=[lstm_size, num_classes],
                                initializer=tf.contrib.layers.xavier_initializer(),
                                regularizer=l2_regularizer(reg_lambda))
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(drop, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores, name='predictions')

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)

            # Weighted loss depending on class frequency
            scale = tf.gather(self.class_weights, self.target_vect)
            self.loss = tf.reduce_mean((losses * scale)) + \
                        sum(tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES))  # Weight Decay
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
