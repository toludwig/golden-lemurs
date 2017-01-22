#!/usr/bin/env python
import requests
from optparse import OptionParser

def split_url(url):
    """
    Splits an URL into username and repo title.
    Correct behaviour is only guarenteed for URLs pointing to the index
    of a github repo.
    """
    # remove trailing slashes
    if url[-1] == '/':
        url = url[:-1]
    split = url.split('/')
    title = split[-1]
    user = split[-2]
    return user, title


def classify():
    parser = OptionParser("usage: %prog [input file] [output file]")

    (options, args) = parser.parse_args()

    with open(args[0], 'r') as urls:
        with open(args[1], 'w') as output:
            for url in urls:
                url = url[:-1]
                name, title = split_url(url)  # cut newline
                rating = requests.get("http://localhost:8081/rate/%s/%s" % (name, title)).json()
                tags = ["DEV", "HW", "EDU", "DOCS", "WEB", "DATA", "OTHER"]
                i = int(rating["Category"])
                print('%s %s' % (url, tags[i - 1]), file=output)

if __name__ == '__main__':
    classify()
