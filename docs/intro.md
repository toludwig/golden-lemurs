Introduction
========

Table of Contents
---------

[**Approach**](/docs/approach)\
[**FFN**](/docs/ffn)\
[**CNN**](/docs/cnn)\
[**RNN**](/docs/rnn)\
[**Ensemble**](/docs/ensemble)\
[**Training**](/docs/training)\
[**Results**](/docs/results)\
[**Discussion**](/docs/discussion)

Abstract
--------

When approaching this competition, we decided early on that various forms of neural networks could be an interesting and powerful solution to the task. We proceeded to seek out state-of-the-art designs of various kinds of neural networks fit to the various forms of data we could extract and developed classifiers building on that.

While some of these classifiers did not fulfill our expectations, we observed great results with convolutional networks applied to word embeddings of READMEs and commit messages. On top of this, we used a deep feed-forward neural classifier to combine the predictions of our sub-nets into a final conclusion instead of using a linear classifier.

For training, we used automatically picked repositories chosen by a heuristic. Our classifier shows good performance and could also be applied to other text classification tasks, although it is hindered by our training dataset which only includes a narrow distribution of repositories.


[Next page: feed-forward network](/docs/ffn)
