Features we consider important
==============================
We decided to focus on the following data fields, which can be grouped into
numerical, textual and temporal ones:
* numerical
  - number of branches
  - number of commits
  - number of contributors
  - number of forks
  - number of issues
  - number of pulls
  - number of stars
  - number of subscribers
* textual
  - README
  - filenames and extensions
  - commits
* temporal
  - times of commits

Especially for the numerical fields, there is no real justification for each of these items yet.
For now we take as much information as we can get and hope
that our classifiers selects the relevant ones. The other groups are more
deliberately chosen...

First of all the README obviously carries very much information.
This is one of the first things you would check as a human after
you have seen the repo name. We will use a classifier to extract
not only keywords, but rather the real semantics using **topic modeling**.

The idea behind the analysis of commit times was, that there are
probably certain time profiles (say within a week), that repeat over the
lifetime of the repository. This could be characteristic for each category,
think of weekly homeworks, as opposed to development repos facing far
more frequent updates.


Classifiers we will use
=======================
We want to work with **Neural Networks**. They are very addaptive
classifiers and model the way humans solve such tasks.
Also there are many possible architectures for such nets, that reflect
the grouping we did above. We will use

* a simple **Feed Forward Network** (FFN) for the numerical data,
* a **Recurrent Neural Network** (RNN) for temporal analysis of commit times, and
* a **Convolutional Neural Network** (CNN) for text mining.

In this way we employ networks of increasing complexity. Instead of
having traditional expert systems, we demonstrate the applicability
and variability of Neural Networks. However, our nets are specialised
each in its input group and yield independent, possible different
category predicitons. To obtain a single prediction for a given repo,
we use yet another network,

* an **ensemble network** that combines the output of the upper ones.

Each of the classifiers, the topologies and the training mechanism
used is described separately in the following sections.

For the implementation we use the Python based **Tensorflow** Framework
for Machine Learning. For a quick introduction, see the excellent
[Tensorflow Tutorials](https://www.tensorflow.org/tutorials/) and of course
the respective parts of our code documentation, especially in `NumericFFN.py`.


Training data mining
====================
We started off by writing a python script (`rate_url.py`) to interactively classify URLs,
which we manually browsed for using Google in order to get representative
amounts of samples for each class, e.g. by searching for 'github physics homeworks' explicitly.
Soon we noticed that this is no satisfactory method to get large amounts of
training data, so we automated the procedure.

We used [GHTorrent](http://ghtorrent.org/) to dump a CSV database of **all (!)**
Github repositories i.e. **39.7 million**, as of January 2017. This CSV
contains all the metadata of every activity on Github, including of course the repository names.
However, we ignore the metadata here, and download only the relevant data later via the API (see below).

Also we had to clean the repository list from forks that have the same READMEs
and contents, in order to not overrepresent vastly forked repositories.

To filter for informative samples for each category we look only at the repository names.
Upon this we run a parsing script `repo_search.py` looking for keywords in their names:

| No. | Category | Keywords           |
|-----|----------|--------------------|
|   1 | DEV      | app, api, lib      |
|   2 | HW       | homework, exercise |
|   3 | EDU      | lecture, teaching  |
|   4 | DOCS     | docs               |
|   5 | WEB      | website, homepage  |
|   6 | DATA     | dataset, sample    |
|   7 | OTHER    | _none_             |

Note that the OTHER category does not need to be learned but rather serves
as a uncertainty indicator for our later classifier.
Thus we obtained JSON files 'dev.json', ..., 'data.json' containing repository URLs
of the same class respectively.

The next step was to download relevant data fields for each repository to learn upon.
Our choice of features we want to train is described the next section.

To access Github repositories we use a Python wrapper for the Github API: [github3](https://github.com/sigmavirus24/github3.py).
This allows us to dump READMEs and all the data fields we specified above.

With the downloaded data we extend our JSON files to 'dev_full.json' etc.
Thus we yield the following training sample format:
    [ 
      {
        "Category":"1",
        "URL":"https://github.com/briantemple/homeworkr",
        "...":"..."
      },
      {...}, ...
    ]

