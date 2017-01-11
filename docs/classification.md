Training data mining
====================
We started off by writing a python script (`rate_url.py`) to interactively classify URLs,
which we manually browsed for using Google in order to get representative
amounts of samples for each class, e.g. by searching for 'github physics homeworks' explicitly.
Soon we noticed that this is no satisfactory method to get large amounts of
training data, so we automated the procedure.

We used [GHTorrent](http://ghtorrent.org/) to dump a CSV database of size (TODO)
containing repositories names.
Upon this we ran a query for keywords in the names using a parser (TODO).

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
This allows us to dump Readmes and metadata like the number of commits and so on.

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
  - readme
  - TODO: what about filenames and extensions?
* temporal
  - times of commits
  - TODO: lifetime (duration)
Database formats
================
The repositories are stored as json
objects in JSON files. The format is like in the following example:
    [ 
      {
        "Category":"1",
        "URL":"https://github.com/briantemple/homeworkr",
        "...":"..."
      },
      {...}, ...
    ]

The /Category/ is encoded numerically where
1 is DEV, 2 is HW, 3 is EDU, 4 is DOCS,
5 is WEB, 6 is DATA and 7 for OTHER.


