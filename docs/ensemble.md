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

This is an easy 
