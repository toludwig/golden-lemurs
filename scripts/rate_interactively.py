import clipboard
from optparse import OptionParser
import json
import logging
from classification.rate_url import download_fields


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
        logging.DEBUG('Did not find file %s. Creating new file' % file)
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

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="out", action="store",
                      type="string", default='./results.json', help="file with results")
    (options, args) = parser.parse_args()

    rate_interactive(options.out)