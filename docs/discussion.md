Discussion
=========

Résumé of our 3 approaches
--------------------------
The word2vec approach we applied to the Commits and the Readme
proved to be highly satisfactory. This is what we expected
because the texts carry really a lot of information.

We are not supprised by the bad performance of the FFN
as we did no data preprocessing and it is in general difficult
to learn on such variable numeric values.

On the other hand we realize that we expected too much
from the commit time data. Therefore it is no wonder
that the LSTM performs badly.

Choice of the Data
------------------
The approach of picking Github repos by searching for keywords
only yields really clear categorizable data. We have caught few
_false positives_ with that. On the other hand we do not cover
cases at the border between two classes that well.

And of course, with more data the classification would improve.
For example repos of category DOCS were underrepresented in our training set.
However, we experienced shortcomings in the data retrieval with the 
Github API. Using a multi-threaded approach running on multiple computers
took us (including debugging of our crawling algorithm) almost
a week.

The boon and bane of semantic analysis
--------------------------------------
We clearly focus 
A problem of this that by only considering semantic information
we fail to see for data formats sometimes, for example we struggle
to classify the websites that are _about_ EDU-, HW- or other content.
While this can be also a pitfall, in general the strength of our
classificator is its focus on the semantics of the texts.
For example repos that look like WEB but are actually hidden


3 Examples of Repos that our classificator is good at
-----------------------------------------------------
1. [https://github.com/MSchuwalow/StudDP]
2. []
