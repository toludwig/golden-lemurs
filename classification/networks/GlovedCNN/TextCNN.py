import tensorflow as tf

from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops


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
                 embedding_size=300):

        self.input_vect = tf.placeholder(tf.float32, [None, sequence_length, embedding_size], name='input')

        self.target_vect = tf.placeholder(tf.int64, [None], name='target')

        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        with tf.name_scope("embedding"):
            self.embedded_chars_expanded = tf.expand_dims(self.input_vect, -1)

        # Convolution and max-pooling Layer
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % i):
                # Convolution Layer
                filter_shape = [filter_size, embedding_size, 1, num_filters]
                w = tf.Variable(tf.truncated_normal(
                    filter_shape, stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")
                conv = tf.nn.conv2d(
                    self.embedded_chars_expanded,
                    w,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")
                # Apply relu
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                # Max-pooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_length - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)
            # Combine all the pooled features
        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(3, pooled_outputs)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])
        self.hidden_layers = []
        for i, num_neurons in enumerate(neurons_hidden):
            with tf.name_scope('fully_connected-%d' % num_neurons):
                w = tf.Variable(tf.truncated_normal([num_filters_total if i == 0 else neurons_hidden[i - 1],
                                                     neurons_hidden[i]], stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[neurons_hidden[i]]), name="b")
                self.hidden_layers.append(tf.nn.relu(tf.nn.xw_plus_b(
                    self.h_pool_flat if i == 0 else self.hidden_layers[-1], w, b, name="ffn")))

        with tf.name_scope('dropout'):
            self.drop = tf.nn.dropout(self.hidden_layers[-1], self.dropout_keep_prob)

        with tf.name_scope("output"):
            w = tf.Variable(tf.truncated_normal([neurons_hidden[-1], num_classes], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.drop, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores)

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            self.loss = tf.reduce_mean(losses)
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
            gradients = optimizer.compute_gradients(self.loss)
            clipped_gradients = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gradients]
            self.train_op = optimizer.apply_gradients(clipped_gradients, global_step=step)

        # Keep track of gradient values and sparsity
        for gradient, variable in gradients:
            if isinstance(gradient, ops.IndexedSlices):
                grad_values = gradient.values
            else:
                grad_values = gradient
            tf.summary.histogram(variable.name, variable)
            tf.summary.histogram(variable.name + "/gradients", grad_values)
            tf.summary.histogram(variable.name + "/gradient_norm", clip_ops.global_norm([grad_values]))
            tf.scalar_summary(variable.name + "/grad/sparsity", tf.nn.zero_fraction(gradient))

        self.merged = tf.summary.merge_all()
