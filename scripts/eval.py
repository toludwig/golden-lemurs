import json


def text_to_json(name, out):
    repos = []
    with open(name, 'r') as file:
        for line in file:
            repos.append(line[:-1]) # cut newline
    with open(out, 'w') as dest:
        json.dump(repos, dest)
