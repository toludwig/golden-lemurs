import json
import re


def main(files):
    extensions = {}
    for file in files:
        with open(file) as f:
            data = json.load(f)

        for repo in data:
            for file in repo['Files']:
                cleaned = re.sub('^.*/', '', file)
                index = cleaned.rfind('.')
                if index == -1:
                    continue
                extension = cleaned[index + 1:]
                if extension not in extensions:
                    extensions[extension] = 1
                else:
                    extensions[extension] += 1

    return extensions
