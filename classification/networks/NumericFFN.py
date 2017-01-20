import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer as xavier
from tensorflow.contrib.layers import l2_regularizer
from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops


class NumericFFN:
    """
    A simple deep feedforward net for general regression
    """
    def __init__(self,
                 parameters,
                 neurons_hidden,
                 categories,
                 learning_rate,
                 reg_lambda):
        """
        :param parameters: number of features in the input layer
        :param neurons_hidden: number of hidden units and layers. list of form [num_layer1, num_layer2, ...]
        :param categories: number of categories in the output layer
        :param learning_rate: learning rate
        :param reg_lambda: L2 regularization value
        """

        self.in_vector = tf.placeholder(tf.float32, [None, parameters], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='target')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.class_weights = tf.placeholder(tf.float32, [categories], name='class_weights')

        self.weights = []

        # Generate Fully Connected Layers
        self.hidden_layers = []
        for i, num_neurons in enumerate(neurons_hidden):
            with tf.variable_scope('fully_connected-%d' % i):

                # We use Xavier initializer instead of sampling from a gaussian
                w = tf.get_variable('W',
                                    shape=(parameters if i == 0 else neurons_hidden[i - 1], neurons_hidden[i]),
                                    initializer=xavier(),
                                    regularizer=l2_regularizer(reg_lambda))

                b = tf.Variable(tf.constant(0.1, shape=[neurons_hidden[i]]), name="b")

                self.hidden_layers.append(tf.nn.relu(tf.nn.xw_plus_b(self.in_vector if i == 0
                                                                     else self.hidden_layers[-1],
                                                                     w,
                                                                     b,
                                                                     name="ffn")))
        # Apply dropout
        with tf.name_scope('dropout'):
            self.drop = tf.nn.dropout(self.hidden_layers[-1], self.dropout_keep_prob)

        # Get output
        with tf.variable_scope("output"):
            w = tf.get_variable('W',
                                shape=[neurons_hidden[-1], categories],
                                initializer=xavier(),
                                regularizer=l2_regularizer(reg_lambda))

            b = tf.Variable(tf.constant(0.1, shape=[categories]), name="b")
            self.scores = tf.nn.xw_plus_b(self.drop, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores, name='predictions')
            self.category = tf.arg_max(self.scores, 1)

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)

            # Weighted loss depending on class frequency
            scale = tf.gather(self.class_weights, self.target_vect)

            self.loss = tf.reduce_mean(losses * scale) + \
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
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5)
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

