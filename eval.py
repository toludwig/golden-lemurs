import requests
from optparse import OptionParser

def split_url(url):
    """
    Splits an URL into username and repo title.
    Correct behaviour is only guarenteed for URLs pointing to the index
    of a github repo.
    """
    split = url.split('/')
    title = split[-1]
    user = split[-2]
    return user, title

def classify():
    parser = OptionParser("usage: %prog [input file] [output file]")
    api = (name, title) => 'http://localhost:8081/%s/%s' % (name, title)

    (options, args) = parser.parse_args()

    with open(args[0], 'r') as urls:
        with open(args[1], 'w' as output:
            for url in urls:
                url = url[:-1]
                name, title = split_url(url) # cut newline
                rating = requests.get(api(name, title)).json()
                tags = ["DEV", "HW", "EDU", "DOCS", "WEB", "DATA", "OTHER"]
                i = int(rating.Category)
                print('%s %s' % (url, tags[i]), file=output)

if __name__ == '__main__':
    classify()
