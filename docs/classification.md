Training data mining
====================
We started off by writing a python script (`rate_url.py`) to classify URLs.
We manually browse for Repos using Google in order to get representative
amounts of samples for each class.
We used [GHTorrent](http://ghtorrent.org/) to query many thousands
of repositories for keywords in their names. TODO
TODO
Our overall objective was to collect more and possibly noisy data
rather than collecting less but reliable, following quantity over quality.


Features we consider important
==============================
To access Github repositories we use the Python API [github3](https://github.com/sigmavirus24/github3.py).
This allows us to dump Readmes and metadata like filenames and extensions.
We decided to focus on the following data fields, which can grouped into
textual and numerical ones:
* textual
  - commits
  - issues
  - readme
* numerical
  - number of commits
  - number of issues
  - number of contributors
  - dates of creation and last commit
TODO
what about filenames and extensions?


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


