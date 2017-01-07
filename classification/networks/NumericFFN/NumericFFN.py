import numpy as np
import tensorflow as tf
import json

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

    def __init__(self):
        self.n_in = 9
        self.n_h1 = 100
        self.n_h2 = 100
        self.n_out= 6

        self.in_vector = tf.placeholder("float", [None, n_in])
        self.target_vector = tf.placeholder("float", [None, n_out])
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        self.weights = {
            'h1' : tf.Variable(tf.random_normal([n_in, n_h1])),
            'h2' : tf.Variable(tf.random_normal([n_h1, n_h2])),
            'out': tf.Variable(tf.random_normal([n_h2, n_out]))
        }

        self.biases = {
            'b1': tf.Variable(tf.random_normal([n_h1])),
            'b2': tf.Variable(tf.random_normal([n_h2])),
            'out': tf.Variable(tf.random_normal([n_out]))
        }

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")
        }
