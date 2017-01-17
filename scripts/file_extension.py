#!/usr/bin/env python

"""
script to count the number of every file extension found in a repository.
Used to generate a table for the Bag-Of-Words model.
"""
import json
import re
from optparse import OptionParser


def count_extensions(files):
    """
    counts the extensions for every repository in every file in the file list.
    :param files: list of files containing repository dumps
    :return: dict containing every found extension
    """
    extensions = {}
    for file in files:
        with open(file) as f:
            data = json.load(f)

        for repo in data:
            for path in repo['Files']:
                cleaned = re.sub('^.*/', '', path)
                index = cleaned.rfind('.')
                if index == -1:
                    continue
                extension = cleaned[index + 1:]
                if extension not in extensions:
                    extensions[extension] = 1
                else:
                    extensions[extension] += 1

    return extensions

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="The json file to count extensions in.")
    (options, args) = parser.parse_args()
    if options.filename is None:
        print('Please provide a filename with the -f parameter')
        exit()
    try:
        print(count_extensions([options.filename]))
    except KeyboardInterrupt:
        print('Invalid File')
