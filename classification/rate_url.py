import sys
import json
import clipboard
from optparse import OptionParser
from .GitHelper import Git
from time import sleep
from multiprocessing import Pool


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
        print("Crawler interrupted @ %s/%s because of %s ; skipping this repo" % (repo['User'], repo['Title'], err))
        return None


def _options():

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
    """
    Gets all data for the repository belonging to the url
    :param url: the url of the repository to get
    :return: dict containing the repository data
    """
    user, title = _split_url(url)

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
    except KeyboardInterrupt as err:
        print("Crawler interrupted @ %s because of %s ; skipping this repo" % (url, err))
        return None
    return obj


def _load(file):
    """
    loads a file as json or creates it if it doesnt exist
    :param file: the file to open
    :return: contents of file or empty list if it doesnt exist
    """
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except Exception:
        print('no data found; creating %s' % file)
        return []


def _save(data, file):
    """
    save json data to file in prettyprint
    :param data: the data to save
    :param file: the file to use
    """
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")


def rate_interactive(file):
    """
    Gets the current url from clipboard, downloads the corresponding repository and queries the user for the category
    :param file: the file to save to
    """
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
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="out", action="store",
                      type="string", default='./results.json', help="file with results")
    (options, args) = parser.parse_args()

    rate_interactive(options.out)

if __name__ == "__main__":
    main()
