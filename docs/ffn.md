Feed Forward Neural Networks
============================

Feed Forward Neural Networks (FFNs) are simple networks of 'neurons' that
take an input, _propagate_ it through some hidden layers
and give you an output for each individual class you specify.
In a way, this structure resembles neurons in the brain, connected by one-way synapses.

![picture of FFN topology](/assets/docs/img/ffn.png)

The topology we use for this is the following:

| input                                 | hidden #1 | hidden #2 | output                         |
|---------------------------------------|-----------|-----------|--------------------------------|
| 8 (as many as we have numeric inputs) |       100 |       100 | 6 (as many as we have classes) |


Activation Function
-------------------
What are these neurons, what functions do they perform?
Well, in our case they are so-called **Rectified Linear Units** (ReLUs).
They get the _weighted sum_ of the output of their predecessor neurons as their input.

$$x_j = \sum_{k=1}^K w_{i,j} y_i$$

On this input $x$ they apply the following activation function:

$$y_j = \mathrm{max}(0, x_j)$$

There are other activation functions which are non-linear but sigmoid like $\mathrm{tanh}$
but this kind of functions lead to the problem of so-called [_vanishing gradients_](https://en.wikipedia.org/wiki/Vanishing_gradient_problem) 
and hence ReLUs are better suited to our needs.


Softmax Layer
-------------
The last layer, i.e. the output layer of the net, has a special task:
It should give us something like a **confidence** for each class, e.g.
35% for DEV. One could also take only the *max* of the outputs
(and say the most active category yields output one and the others zero)
but it is easier to train the network with a derivable function.
And this is why you use softmax as the activation function in the last layer:

$$y_j = \frac{e^{x_j}}{\sum_{k=1}^K e^{x_k}}$$

What it does is normalizing the inputs so that the outputs sum up to one
and we get nice percentages.


