Testing the nets
================

Recap of the training
---------------------
The **accuracy** is defined as the ratio of rightly predicted categories to all the samples.
During the training we plotted the current accuracy with respect to
the training data to see when the network stops to make progress with learning.

According to this we could decide, which networks to drop from our final classifier.
These are the FFN which performed very low (accuracy of ~30%)
and the LSTM which stoped at roughly ~50%.

For illustration here are the training plots. One can see how fast the CNNs
converge. The upper graph is for the README and the one below for the commit CNN:

![picture of learning progress](/assets/docs/img/learning_progress.png)


Testing the nets
----------------
After training, of course we have to validate the networks against
the **test data**, the 10% of our data that the net has never seen before.

Here we list the performance of all the networks on our own test data (not "Anhang B"!):

| Network      | Performance |
|--------------|-------------|
| CNN (README) |         83% |
| CNN (Commit) |         60% |
| Ensemble     |         90% |

For further data, please have a look at our Tensorboard documentation.

[Previous page: The ensemble](/docs/ensemble)\
[Next page: Discussion](/docs/discussion)\
[Table of Contents](/docs/abstract)
