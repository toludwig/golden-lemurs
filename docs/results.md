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

![](/assets/docs/img/learning_progress.png)


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

## Results on appendix B

Total: 31
Correct: 24
Wrong: 7
Yield: 77.4%
Precision: 
HW: 2 correct out of 5
DEV: 5 correct out of 8
EDU: 5 out of 5
WEB: 4 out of 4
DATA: 3 out of 3
DOCS: 3 out of 6
OTHER: 1 out of 1


[Previous page: The ensemble](/docs/ensemble)\
[Next page: Discussion](/docs/discussion)\
[Table of Contents](/docs/intro)
