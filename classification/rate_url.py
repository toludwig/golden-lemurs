import json
from .GitHelper import fetch_repo
from multiprocessing import Pool
import logging

logger = logging.getLogger(__name__)


def add_enrichment(file, out, size, action):
    """
    Read from a file containing a list, apply a given operation on every entry, save the result to a file
    after n timesteps.
    :param file: the file to read from
    :param out: the file to save to
    :param size: saving interval/ size of processing batch
    :param action: the function to perform on every entry
    :return:
    """
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
        logger.info('Saving data.')
        _save(data, file)
        _save(new, out)


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


def download_fields(url):
    """
    Gets a repo for a given url
    :param url: the url
    :return: dict representing the repo
    """
    user, title = split_url(url)
    logging.info('crawling %s/%s.' % (user, title))
    try:
        repo = fetch_repo(user, title)
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
    add_enrichment(file, out, 32, download_fields)
    data = _load(out)
    for repo in data:
        repo['Category'] = category
    _save(data, out)
