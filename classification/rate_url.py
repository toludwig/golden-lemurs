import json
from .GitHelper import Git
from multiprocessing import Pool
import logging
import time

logger = logging.getLogger(__name__)


def add_enrichment(file, out, size, action):
    data = _load(file)
    new = _load(out)
    for batch in [data[i:i+size] for i in range(0, len(data), size)]:
        addition = []
        try:
            with Pool(processes=8) as executor:
                addition += list(executor.imap(action, batch))
        except Exception:
            logger.exception('Unhandled exception in action. Data was not saved')
            raise
        downloaded = [i for i, elem in enumerate(addition) if addition[i] is not None]
        data = [data[i] for i, elem in enumerate(data) if i not in downloaded]
        new += list(filter(None, addition))
        _save(data, file)
        _save(new, out)


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
    repo = {}
    repo["User"], repo["Title"] = _split_url(url)
    logging.info('crawling %s/%s.' % (repo['User'], repo['Title']))
    try:
        git = Git(repo["User"], repo["Title"])
        if not git.valid():
            return None
        repo["Readme"] = git.get_readme()
        repo["NumberOfContributors"] = git.number_contributors()
        repo["Branches"] = git.number_branches()
        repo["Forks"] = git.number_forks()
        repo["Stars"] = git.number_stars()
        repo["Pulls"] = git.number_pull_requests()
        repo["Subscribers"] = git.number_subscribers()
        repo["NumberOfCommits"], repo["CommitTimes"], repo["CommitMessages"] = git.get_commits()
        repo["Times"] = git.get_times()
        repo["Files"] = git.get_files()
    except TimeoutError:
        logging.exception('Could not get all data for %s' % url)
        return None
    return repo


def _load(file):
    """
    loads a file as json or creates it if it doesnt exist
    :param file: the file to open
    :return: contents of file or empty list if it doesnt exist
    """
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug('Did not find file %s. Creating new file' % file)
        return []


def _save(data, file):
    """
    save json data to file in prettyprint
    :param data: the data to save
    :param file: the file to use
    """
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")


def from_url_list(file, out, category):
    add_enrichment(file, out, 24, download_fields)
    data = _load(out)
    for repo in data:
        repo['Category'] = category
    _save(data, out)
