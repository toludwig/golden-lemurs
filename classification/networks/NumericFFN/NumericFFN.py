import tensorflow as tf

from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops

'''
A simple FF net for the numerical fields of a repo, i.e.
- number of branches
- number of contributors
- number of commits
- number of issues
- number of forks
- number of pulls
- number of stars
- number of subscribers
- activity duration (last-activity - creation)
'''


class NumericFFN:
    """
    Neural Network performing Logistic Regression
    """
    def __init__(self,
                 parameters,
                 neurons_hidden,
                 categories,
                 learning_rate):

        self.in_vector = tf.placeholder(tf.float32, [None, parameters], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='target')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.class_weights = tf.placeholder(tf.float32, [categories], name='class_weights')

        self.hidden_layers = []
        for i, num_neurons in enumerate(neurons_hidden):
            with tf.name_scope('fully_connected-%d' % num_neurons):
                w = tf.Variable(tf.truncated_normal([parameters if i == 0 else neurons_hidden[i - 1],
                                                     neurons_hidden[i]], stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[neurons_hidden[i]]), name="b")
                self.hidden_layers.append(tf.nn.relu(tf.nn.xw_plus_b(
                    self.in_vector if i == 0 else self.hidden_layers[-1], w, b, name="ffn")))

        with tf.name_scope('dropout'):
            self.drop = tf.nn.dropout(self.hidden_layers[-1], self.dropout_keep_prob)

        with tf.name_scope("output"):
            w = tf.Variable(tf.truncated_normal([neurons_hidden[-1], categories], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[categories]), name="b")
            self.scores = tf.nn.xw_plus_b(self.drop, w, b, name="scores")
            self.predictions = tf.nn.softmax(self.scores)
            self.category = tf.arg_max(self.scores, 1)

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            scale = tf.gather(self.class_weights, self.target_vect)
            self.loss = tf.reduce_mean(losses * scale)
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

