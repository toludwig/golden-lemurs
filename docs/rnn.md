Recursive Neural Networks
=========================

So far we were concerned with networks that get a inputs
of a fixed size. But sometimes we just don't know their size,
mostly in cases of (temporal) sequences.
That's what Recursive Neural Networks (RNNs) are best suited for,
data that exhibits patterns over time. They find applications in
recognition of (handwritten) text and speech, or at the stock market.
For this they have a special ability, they 'save' previous input.
As the name suggests, they have recurrent 'synapses', i.e. edges
going back in circles to the same cell. Here is how it looks if
you unfold this circle three times [^1]:

![picture of RNN](/assets/docs/img/rnn.jpg)


The Long Short-Term Memory net
==============================

However, the trouble with most types of RNNs is that they are essentially unable
to remember things in long term, e.g. words that occurred sentences ago.
This is due to the _vanishing gradients problem_ and was first formerly proven by
[Hochreiter in 1991](people.idsia.ch/~juergen/SeppHochreiter1991ThesisAdvisorSchmidhuber.pdf).
In 1997 appeared an often-cited [followup paper](http://www.mitpressjournals.org/doi/10.1162/neco.1997.9.8.1735#.WH4Lg2c_3qM),
also by Hochreiter and Schmidhuber, introducing the **Long Short-Term
Memory (LSTM)** that is designed to tackle this shortcoming.

This does no longer look like a real network but rather like a sequence of cells.

________________________________

[^1]: source: http://www.wildml.com/2015/09/recurrent-neural-networks-tutorial-part-1-introduction-to-rnns/
generierung via for file in *.md; pandoc --mathjax -o $file.html $file; end;
/assets/docs/{bild}
/docs/{name (ohne endung)}
