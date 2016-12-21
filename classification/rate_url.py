#!/usr/bin/python3
import sys
import simplejson as json
import clipboard
from optparse import OptionParser
from .GitHelper import Git

def _options():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="out", action="store",
                      type="string", default='./results.json', help="file to write to")

    return parser.parse_args()

def _split_url(url):
    """
    Splits an URL into username and repo title.
    Correct behaviour is only guarenteed for URLs pointing to the index
    of a github repo.
    """
    split = url.split('/')
    title = split[4]
    user = split[3]
    return (user, title)

def download_fields(url):
    user, title = _split_url(url)
    git = Git(user, title)
    obj = {}
    obj["URL"] = url
    obj["User"]                 = user
    obj["Title"]                = title
    obj["Readme"]               = git.get_readme()
    obj["NumberOfContributors"] = git.number_contributors()
    obj["NumberCommits"]        = git.number_commits()
    obj["Commits"]              = git.get_commits()
    obj["NumberIssues"]         = git.number_issues()
    obj["Issues"]               = git.get_issues()
    obj["Times"]                = git.get_times()
    return obj

def _save(data, file):
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")

def main():
    (options, args) = _options()
    results = []
    clipboard.copy('')

    while True:
        url = ""
        while url == '':
            url = clipboard.paste()
        print("URL: %s" % url)

        trying = True
        while trying:
            c = input("Ratings: [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER [S]kip [Q]uit\n")
            if c in ['q', 'Q']:
                _save(results, options.out)
                return
            elif c in ['s', 'S']:
                trying = False
            elif c in ['1', '2', '3', '4', '5', '6', '7']:
                trying = False
                cur_obj = download_fields(url)
                cur_obj["Category"] = c
                results.append(cur_obj)


def extend_fields(in_file):
    '''
    Function for adding the downloaded fields
    for classified JSON data with only URL and Category
    '''
    with open(in_file, 'r') as f:
        results = json.load(f)
    # download fields for each object
    for i, obj in enumerate(results):
        results[i] = download_fields(obj['URL'])
    return results

if __name__ == "__main__":
    main()
