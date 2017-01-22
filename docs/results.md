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

| URL                                                           | OUR GUESS | OUR CLASSIFICATION | MATCH |
|---------------------------------------------------------------|-----------|--------------------|-------|
| https://github.com/ga-chicago/wdi5-homework                   | HW        | HW                 | ✓     |
| https://github.com/Aggregates/MI_HW2                          | HW        | EDU                | ✗     |
| https://github.com/datasciencelabs/2016                       | EDU       | EDU                | ✓     |
| https://github.com/githubteacher/intro-november-2015          | EDU       | EDU                | ✓     |
| https://github.com/atom/atom                                  | DEV       | DEV                | ✓     |
| https://github.com/jmcglone/jmcglone.github.io                | WEB       | WEB                | ✓     |
| https://github.com/hpi-swt2-exercise/java-tdd-challenge       | HW        | HW                 | ✓     |
| https://github.com/alphagov/performanceplatform-documentation | DOCS      | DOCS               | ✓     |
| https://github.com/harvesthq/how-to-walkabout                 | OTHER     | OTHER              | ✓     |
| https://github.com/vhf/free-programming-books                 | WEB       | WEB                | ✓     |
| https://github.com/d3/d3                                      | DEV       | DEV                | ✓     |
| https://github.com/carlosmn/CoMa-II                           | HW        | EDU                | ✗     |
| https://github.com/git/git-scm.com                            | WEB       | WEB                | ✓     |
| https://github.com/PowerDNS/pdns                              | DEV       | DOCS               | ✗     |
| https://github.com/cmrberry/cs6300-git-practice               | HW        | EDU                | ✗     |
| https://github.com/Sefaria/Sefaria-Project                    | DATA      | DATA               | ✓     |
| https://github.com/mongodb/docs                               | DOCS      | DOCS               | ✓     |
| https://github.com/sindresorhus/eslint-config-xo              | DOCS      | DOCS               | ✓     |
| https://github.com/e-books/backbone.en.douceur                | DOCS      | DEV                | ✗     |
| https://github.com/erikflowers/weather-icons                  | DEV       | DEV                | ✓     |
| https://github.com/tensorflow/tensorflow                      | DEV       | DEV                | ✓     |
| https://github.com/cs231n/cs231n.github.io                    | EDU       | EDU                | ✓     |
| https://github.com/m2mtech/smashtag-2015                      | EDU       | EDU                | ✓     |
| https://github.com/openaddresses/openaddresses                | DEV       | DEV                | ✓     |
| https://github.com/benbalter/congressional-districts          | DATA      | DATA               | ✓     |
| https://github.com/Chicago/food-inspections-evaluation        | DOCS      | DOCS               | ✓     |
| https://github.com/OpenInstitute/OpenDuka                     | DATA      | DATA               | ✓     |
| https://github.com/torvalds/linux                             | DEV       | DOCS               | ✗     |
| https://github.com/bhuga/bhuga.net                            | WEB       | WEB                | ✓     |
| https://github.com/macloo/just_enough_code                    | EDU       | EDU                | ✓     |
| https://github.com/hughperkins/howto-jenkins-ssl              | DOCS      | WEB                | ✗     |

Yield (for all categories):

| Total   |    31 |
| Correct |    24 |
| Wrong   |     7 |
| Yield   | 77.4% |

Precision (for each category):

| Category | RIGHT | TOTAL |
|----------|-------|-------|
| HW       |     2 |     5 |
| DEV      |     5 |     8 |
| EDU      |     5 |     5 |
| WEB      |     4 |     4 |
| DATA     |     3 |     3 |
| DOCS     |     3 |     6 |
| OTHER    |     1 |     1 |


*****


[Previous page: The ensemble](/docs/ensemble)\
[Next page: Discussion](/docs/discussion)\
[Table of Contents](/docs/intro)
