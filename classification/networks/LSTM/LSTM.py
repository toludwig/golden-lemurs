import tensorflow as tf

class LSTM:

    def __init__(self,
                 num_layers,
                 hidden_size,
                 batch_size,
                 num_classes,
                 series_length):

        self.input_vect = tf.placeholder(tf.float32, [None, series_length], name='input')
        self.target_vect = tf.placeholder(tf.int64, [None], name='labels')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        input_list = tf.unpack(tf.expand_dims(self.input_vect, 2), 1)

        # LSTM Layers
        with tf.name_scope('LSTM'):
            cell = tf.nn.rnn_cell.LSTMCell(hidden_size)
            cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=self.dropout_keep_prob)
            cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_layers)
            initial_state = cell.zero_state(batch_size, tf.float32)
            self.lstm, _ = tf.nn.seq2seq.rnn_decoder(input_list, initial_state, cell)

        # Output Layer
        with tf.name_scope('output'):
            w = tf.Variable(tf.truncated_normal([hidden_size, num_classes], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            self.scores = tf.nn.xw_plus_b(self.lstm[1], w, b, name='scores')
            self.predictions = tf.argmax(self.scores, 1, name='predictions')

        # CalculateMean cross-entropy loss
        with tf.name_scope('loss'):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(self.scores, self.target_vect)
            self.loss = tf.reduce_sum(losses) / batch_size

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(tf.argmax(tf.nn.softmax(self.scores), 1), self.target_vect)
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")

