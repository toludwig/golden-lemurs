import numpy as np
import tensorflow as tf
import json
from .settings import FEATURES

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


def repo_params(dict):
    data = []
    for key in FEATURES:
        data.append(dict[key])
    return data


class NumericFFN:
    """
    Neural Network performing Logistic Regression
    """
    def __init__(self,
                 parameters,
                 neurons_hidden,
                 categories):

        self.in_vector = tf.placeholder(tf.float32, [None, parameters], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='target')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

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
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            self.loss = tf.reduce_mean(losses)

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")
