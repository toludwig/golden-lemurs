The Ensemble Network
====================

After training of all the networks we needed to make a decision:
Which networks are worthy to be integrated in the final classificator
regarding accuracy but also regarding the amount of computation time.

We choosed only the following two networks:

* the CNN for README
* and the CNN for the Commit times.

These give us their predictions and we feed them into our master net,
the Ensemble Network.

This is an easy two-layer _feed forward_ topology for learning
non-linear weightings of the CNN predictions. For example it should
learn to rely only on the Commits if the README is empty.

[Previous page: Recurrent networks](/docs/rnn)\
[Next page: Training our networks](/docs/training)\
[Table of Contents](/docs/abstract)
