#!/usr/bin/python3
import sys
import json
import clipboard
from optparse import OptionParser
from .GitHelper import Git
from random import sample
from time import sleep
from multiprocessing import Pool


def load_data(repos, results, category, size=100):
    data = _load(repos)
    if data == []:
        return False
    new = _load(results)
    try:
        with Pool(processes=8) as executor:
            new += list(executor.imap(download_fields, data[:size]))
        for repo in new:
            if repo is not None:
                repo["Category"] = category
    except (KeyboardInterrupt, Exception):
        raise Exception("Crawler interrupted").with_traceback(sys.exc_info()[2])
    downloaded = [i for i, elem in enumerate(new) if new[i] is not None]
    _save([data[i] for i, elem in enumerate(data) if i not in downloaded], repos)
    _save(list(filter(None, new)), results)
    return True


def get_files(repo):
    def action(r, git):
        r['Files'] = git.get_files()

    return enrich_entry(repo, action)


def add_files(file, out, size=100):
    return add_enrichment(file, out, size, get_files)


def add_enrichment(file, out, size, action):
    data = _load(file)
    if data == []:
        return False
    new = _load(out)
    addition = []
    try:
        with Pool(processes=8) as executor:
            addition += list(executor.imap(action, data[:size]))
    except:
        raise Exception("Crawler interrupted").with_traceback(sys.exc_info()[2])
    downloaded = [i for i, elem in enumerate(addition) if addition[i] is not None]
    _save([data[i] for i, elem in enumerate(data) if i not in downloaded], file)
    _save(new + list(filter(None, addition)), out)
    return True


def enrich_entry(repo, action):
    print(repo['Title'])
    connected = False
    while not connected:
        try:
            git = Git(repo["User"], repo["Title"])
            connected = True
        except Exception:
            sleep(10)

    if not git.valid():
        return None
    try:
        action(repo, git)
        return repo
    except Exception as err:
        print("Crawler interrupted @ %s because of %s ; skipping this repo" % (repo["Url"], err))
        return None


def _options():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="out", action="store",
                      type="string", default='./results.json', help="file with results")
    parser.add_option("-r", "--repos", dest="list", action="store",
                      type="string", default='./list.json', help="file with repo urls; default: reads clipboard")
    parser.add_option("-c", "--category", dest="category", action="store", type="string", default='0',
                      help="category to assign; default: console input")
    parser.add_option("-n", "--number", dest="number", action="store", type="int", default=50,
                      help="number of repos to download")

    return parser.parse_args()


def _split_url(url):
    """
    Splits an URL into username and repo title.
    Correct behaviour is only guarenteed for URLs pointing to the index
    of a github repo.
    """
    split = url.split('/')
    title = split[-1]
    user = split[-2]
    return user, title


def download_fields(url):
    user, title = _split_url(url)
    print('%s/%s' % (user, title))

    # Api rate limit might have been reached
    connected = False
    while not connected:
        try:
            git = Git(user, title)
            connected = True
        except:
            sleep(10)
    if not git.valid():
        return None
    try:
        # skip forks as heuristic to avoid training on duplicate data
        obj = {}
        obj["User"] = user
        obj["Title"] = title
        obj["Readme"] = git.get_readme()
        obj["NumberOfContributors"] = git.number_contributors()
        obj["Branches"] = git.number_branches()
        obj["Forks"] = git.number_forks()
        obj["Stars"] = git.number_stars()
        obj["Pulls"] = git.number_pull_requests()
        obj["Subscribers"] = git.number_subscribers()
        obj["NumberOfCommits"], obj["CommitTimes"], obj["CommitMessages"] = git.get_commits()
        obj["Times"] = git.get_times()
        obj["Files"] = git.get_files()
    except Exception as err:
        print("Crawler interrupted @ %s because of %s ; skipping this repo" % (url, err))
        return None
    return obj


def _load(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except Exception:
        print('no data found; creating %s' % file)
        return []


def _save(data, file):
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")


def rate_interactive(file):
    results = _load(file)
    last_url = ''
    try:
        clipboard.copy('')

        while True:
            url = ""
            while url == '':
                url = clipboard.paste()
            print("URL: %s" % url)
            last_url = url

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
                    if cur_obj is not None:
                        cur_obj["Category"] = c
                        results.append(cur_obj)
                    else:
                        print("Repo invalid: %s" % url)
    except (KeyboardInterrupt, Exception):
        _save(results, file + '.bak')
        raise Exception("Crawler interrupted @ %s" % last_url).with_traceback(sys.exc_info()[2])


def main():
    (options, args) = _options()

    if options.category != '0':  # category given, automatic
        load_data(options.list, options.out, options.category, options.number)
    else:  # wait on paste
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
