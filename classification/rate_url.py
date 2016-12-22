#!/usr/bin/python3
import sys
import json
import clipboard
from optparse import OptionParser
from .GitHelper import Git

def load_data(repos, results, category):
    data = _load(results)
    try:
        with open(repos, 'r') as file:
            urls = json.load(file)
            for url in urls:
                repo = download_fields(url, 'api')
                if repo != None:
                    repo["Category"] = category
                    data.append(repo)
                else:
                    print("Repo invalid: %s" % url)
    except KeyboardInterrupt:
        _save(data, results + '.bak')
    _save(data, results)

def _options():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="out", action="store",
                      type="string", default='./results.json', help="file with results")
    parser.add_option("-r", "--repos", dest="list", action="store",
                      type="string", default='./list.json', help="file with repo urls; default: reads clipboard")
    parser.add_option("-c", "--category", dest="category", action="store", type="string", default='0', help="category to assign; default: console input")

    return parser.parse_args()

def _split_api_url(url):
    """
    Splits an URL into username and repo title.
    Correct behaviour is only guarenteed for URLs similiar to https://api.github.com/repos/{user}/{title}
    """
    split = url.split('/')
    title = split[5]
    user = split[4]
    return (user, title)

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


def download_fields(url, url_schema = 'web'):
    if url_schema == 'web':
        user, title = _split_url(url)
    elif url_schema == 'api':
        user, title = _split_api_url(url)
    else:
        raise Exception('no such url schema')
    git = Git(user, title)
    if git.valid:
        obj = {}
        obj["User"] = user
        obj["Title"] = title
        obj["Readme"] = git.get_readme()
        obj["NumberOfContributors"] = git.number_contributors()
        obj["Commits"] = git.get_commits()
        obj["Issues"] = git.get_issues()
        obj["Times"] = git.get_times()
        return obj
    else:
        return None

def _load(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        print('no data found; creating %s' % file)
        return []

def _save(data, file):
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")

def rate_interactive(file):
    results = _load(file)
    try:
        clipboard.copy('')

        while True:
            url = ""
            while url == '':
                url = clipboard.paste()
            print("URL: %s" % url)

            trying = True
            while trying:
                c = input(
                    "Ratings: [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER [S]kip [Q]uit\n")
                if c in ['q', 'Q']:
                    _save(results, file)
                    return
                elif c in ['s', 'S']:
                    trying = False
                elif c in ['1', '2', '3', '4', '5', '6', '7']:
                    trying = False
                    cur_obj = download_fields(url)
                    if cur_obj != None:
                        cur_obj["Category"] = c
                        results.append(cur_obj)
                    else:
                        print("Repo invalid: %s" % url)
    except KeyboardInterrupt:
        _save(results, file + '.bak')

def main():
    (options, args) = _options()

    if options.category != '0': # category given, automatic
        load_data(options.list, options.out, options.category)
    else: # wait on paste
        rate_interactive(options.out)


# legacy, needed?
# def extend_fields(in_file):
#     '''
#     Function for adding the downloaded fields
#     for classified JSON data with only URL and Category
#     '''
#     with open(in_file, 'r') as f:
#         results = json.load(f)
#     # download fields for each object
#     for i, obj in enumerate(results):
#         results[i] = download_fields(obj['URL'])
#     return results

if __name__ == "__main__":
    main()
