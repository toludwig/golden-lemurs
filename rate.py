#!/bin/python
import sys
import json
from optparse import OptionParser

IN_FILE="repos.json"
OUT_FILE="results.json"
USER=0

RESULTS= { "progress": [0, 0, 0], "ratings": [] }
REPOS=None
PROGRESS=0
BATCH_SIZE=0
OFFSET=0

def options():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="input", type="string",
                      help="dump of json repos to rate", metavar="FILE")
    parser.add_option("-u", "--user", dest="user", type="int", help="id of user: 0,1,2 (for task separation)")
    parser.add_option("-o", "--output", dest="out", type="string", help="file to write to")

    params =  parser.parse_args()[0]
    if params.input is not None:
        IN_FILE = params.input
    if params.out is not None:
        OUT_FILE = params.out
    if params.user is not  None:
        USER = int(params.user) % 3

def read():
    global REPOS, BATCH_SIZE, PROGRESS, OFFSET, RESULTS
    with open(IN_FILE, "r") as f:
        REPOS = json.load(f)
        BATCH_SIZE = len(REPOS) // 3
    with open(OUT_FILE, "r") as f:
        RESULTS = json.load(f)
        print(RESULTS)
        PROGRESS = RESULTS['progress'][USER]
        OFFSET = BATCH_SIZE * USER

def save():
    RESULTS['progress'][USER] = PROGRESS
    print(RESULTS)
    with open(OUT_FILE, "w") as f:
        json.dump(RESULTS, f)

def next_dataset():
    global PROGRESS
    if PROGRESS == BATCH_SIZE - 1:
        return None
    data = REPOS[OFFSET + PROGRESS]
    PROGRESS += 1
    return data

def rate(rating):
    RESULTS['ratings'].append({"id": REPOS[OFFSET + PROGRESS-1]["ID"], "rating": rating})

def main():
    options()
    read()

    data = next_dataset()
    while data != None:
        for i in range(100):
            print()
        print("Repo: %s\n" % data['Name'])
        step = 1000
        pos = min(step, len(data['Readme']))
        print(data['Readme'][0:pos])
        while True:
            print("\nRatings: [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER [D]rop [M]ore [Q]uit")
            c = sys.stdin.read(1)
            if c in ['1', '2', '3', '4', '5', '6', '7']:
                rate(int(c))
                break
            elif c in ['d', 'D']:
                #skip
                break
            elif c in ['m', 'M']:
                pos = min(pos+step, len(data['Readme']))
                print(data['Readme'][max(pos-step, 0):pos])
            elif c in ['q', 'Q']:
                global PROGRESS
                PROGRESS -= 1
                save()
                return
            else:
                pass
        data = next_dataset()

    save()

if __name__ == '__main__':
    main()
