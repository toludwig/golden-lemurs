Recurrent Neural Networks
=========================

So far we were concerned with networks that get inputs
of a fixed size. But sometimes we just don't know their size,
mostly in cases of (temporal) sequences.
That's what Recurrent Neural Networks (RNNs) are best suited for,
data that exhibits patterns over time. They find applications in
recognition of (handwritten) text and speech, or at the stock market.
For this they have a special ability, they 'save' previous input.
As the name suggests, they have recurrent 'synapses', i.e. edges
going back in circles to the same cell. Here is how it looks if
you unfold this circle three times [[1]]:
![picture of RNN](/assets/docs/img/rnn.jpg)


The Long Short-Term Memory net
==============================

However, the trouble with most types of RNNs is that they are essentially unable
to remember things in long term, e.g. words that occurred sentences ago.
This is due to the _vanishing gradients problem_ and was first formerly proven by
[Hochreiter in 1991](http://people.idsia.ch/~juergen/SeppHochreiter1991ThesisAdvisorSchmidhuber.pdf).
In 1997 appeared an often-cited [followup paper](http://www.mitpressjournals.org/doi/10.1162/neco.1997.9.8.1735#.WH4Lg2c_3qM),
also by Hochreiter and Schmidhuber, introducing the **Long Short-Term
Memory (LSTM)** that is designed to tackle this shortcoming.

Its nodes do no longer look like simple neurons, but rather like complex
**memory cells**, here again unfolded [[2]]:
![picture of LSTM](/assets/docs/img/LSTM.png)

Each cell gets its memory $C$ from its earlier state, shown by the continuous horizontal
line at the top. Further, this state can be influenced by new inputs $x$ which can
be whole vectors. But they are weighted by certain gates, depicted by $\sigma$ or $\tanh$.
Internally these gates consist of a layer of neurons with sigmoid activation functions
that squash the input values in ranges of [0, 1] or [-1, 1] respectively.
The following list explains what is going on in the cell from left to right:

* The first filtering is done by the so-called _forget gate_ on the very left. It
decides how much information from the old state is being kept with respect to the
current input.

* Secondly, we want to integrate the new input at the _input gate_.
To do so, first we decide which values are to be updated ($\sigma$ branch) while
at the same time creating new candidate values ($\tanh$ branch) and later combine
both branches by pointwise vector multiplication to finally update the state.

* At last, we have to filter the current state to produce an output $h$.
Again we apply a layer of $\tanh$ to normalize the state and $\sigma$ to select the
relevant output with respect to the current input.

Our LSTM for commit-time analysis
=================================

In fact, this is only the main principle of how LSTMs are designed but in practice
there are variable implementations. For example, we use a version called
**Bidirectional LSTM** (BLSTM), which takes into account not only states from previous inputs
but also looks ahead and considers 'future' input. This of course is possible
because we have the whole sequence of commits given (no realtime analysis)
which we can feed into the net from both directions, once forwards once backwards.
The BLST actually consists of two separate LSTMS, one for each direction.
These LSTM cells are independent from each other, they do not communicate,
but only their outputs are concatenated.

Data preprocessing
------------------
From our [Training Data Mining](/docs/approach) we have given a list of commit
timestamps within the whole lifetime of each repo.
The objective was to create a time profile for a period of a week or a month
to see how commits are distributed, maybe even detect class-specific peaks.
The function for the preprocessing basically does a binning of our list, it
can be found here: `networks.Data.commit_time_profile`. It yields histograms like
these, here for the classes DEV and HW:
![picture of commit profiles](/assets/docs/img/commit_time_profiles.png)

Unfortunately, as one might suspect from the graphs, there does not
really seem to be that much information in the commit times with regard
to the categories. Also there are many sparse profiles of repos with very
few commits.

In fact, we realized after training that the net did not perform particularly
well and decided to drop the LSTM from our later classificator, it will not occur
in the results.


[1]: http://www.nature.com/nature/journal/v521/n7553/abs/nature14539.html

[2]: http://colah.github.io/posts/2015-08-Understanding-LSTMs/

[Previous page: Convolutional networks](/docs/cnn)\
[Next page: Ensemble network](/docs/ensemble)
