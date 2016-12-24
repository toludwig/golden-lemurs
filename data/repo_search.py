#!/usr/bin/env python
import csv
import json
from os.path import join

def search_repos(my_filter, my_map, file=join(__package__, 'projects.csv')):
    list = []
    with open(file, newline='') as csvfile:
        repos = csv.reader(csvfile, doublequote=False,escapechar='\\', quoting=csv.QUOTE_NONNUMERIC)
        for repo in repos:
            if my_filter(repo):
                list.append(my_map(repo))
    return list

def save_search(file, keywords):
    def match(repo):
        for key in keywords:
            if key in repo[3]: # index 3 = name
                return True
        return False

    repos = search_repos(match, lambda r: r[1]) # index 1 = url
    with open(file, 'w') as homeworks:
        json.dump(repos, homeworks)

def list_repos():
    categories = [
        ['edu.json', ['lecture', 'course', 'teaching']],
        ['homework.json', ['homework', 'exercise']],
        ['web.json', ['website', 'homepage']],
        ['docs.json', ['docs']],
        ['data.json', ['dataset', 'data_', 'data-', 'sample']]
    ]
    for entry in categories:
        file = entry[0]
        keys = entry[1]
        print('filling %s' % file)
        save_search(join(__package__, file), keys)

if __name__ == '__main__':
    list_repos()
