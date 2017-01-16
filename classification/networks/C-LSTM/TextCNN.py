import tensorflow as tf

from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops
from tensorflow.contrib.layers import l2_regularizer

class TextCNN:
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    def __init__(self,
                 sequence_length,
                 num_classes,
                 filter_sizes,
                 num_filters,
                 neurons_hidden,
                 learning_rate,
                 embedding_size,
                 reg_lambda,
                 num_layers=3,
                 series_length=0,
                 lstm_size=100):

        self.input_vect = tf.placeholder(tf.float32, [None, sequence_length, embedding_size], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='target')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.class_weights = tf.placeholder(tf.float32, [num_classes], name='class_weights')
        self.batch_size = tf.placeholder(tf.int32, name='batch_size')

        self.weights = []

        with tf.name_scope("embedding"):
            self.embedded_chars_expanded = tf.expand_dims(self.input_vect, -1)

        # Convolution and max-pooling Layer
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.variable_scope("conv-maxpool-%s" % i):

                # Convolution Layer
                filter_shape = [filter_size, embedding_size, 1, num_filters]
                w = tf.get_variable("W", shape=filter_shape,
                                    initializer=tf.contrib.layers.xavier_initializer_conv2d())

                b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")

                conv = tf.nn.conv2d(
                    self.embedded_chars_expanded,
                    w,  # Uses the kernel widths defined in filter sizes
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")

                # Apply relu
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")

                # Max-pooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_length - filter_size + 1, 1, 1],  # Shape is due to valid padding
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)

        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(3, pooled_outputs)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

        # LSTM Layers
        with tf.name_scope('LSTM'):
            cell = tf.nn.rnn_cell.LSTMCell(lstm_size,
                                           initializer=tf.contrib.layers.xavier_initializer())
            """
            No need for regularization here as the LSTMs inner architecture prevents gradient vanishing. exploding
            gradients are dealt with by gradient clipping.
            """

            cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=self.dropout_keep_prob)
            multi_cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_layers)  # This creates deep rnn layers
            state = multi_cell.zero_state(self.batch_size, tf.float32)
            self.lstm, state = multi_cell(self.h_pool_flat, state)

        with tf.variable_scope("output"):
            w = tf.get_variable('W',
                                shape=[lstm_size, num_classes],
                                initializer=tf.contrib.layers.xavier_initializer(),
                                regularizer=l2_regularizer(reg_lambda))
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.lstm, w, b, name="scores")
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
