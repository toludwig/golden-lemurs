#!/usr/bin/python3
import sys
import json
import clipboard
from optparse import OptionParser
from .GitHelper import Git

OUT_FILE="results.json"
RESULTS=[]

def options():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="out", type="string", help="file to write to")

    params = parser.parse_args()[0]
    if params.out is not None:
        OUT_FILE = params.out

def split_url(url):
    split = url.split('/')
    title = split[-1]
    user = split[-2]
    return (user, title)

def save():
    with open(OUT_FILE, "w") as f:
        json.dump(RESULTS, f)

def download_fields(obj):
    print(obj["URL"])
    user, title = split_url(obj["URL"])
    git = Git(user, title)
    obj["User"]                 = user
    obj["Title"]                = title
    obj["Readme"]               = git.get_readme()
    obj["NumberOfContributors"] = git.number_contributors()
    obj["NumberCommits"]        = git.number_commits()
    obj["Commits"]              = git.get_commits()
    obj["NumberIssues"]         = git.number_issues()
    obj["Issues"]               = git.get_issues()
    obj["Times"]                = git.get_times()
    return obj

def main():
    options()
    url = ""

    while True:
        cur_obj={}

        print("\nURL: ")
        while url == clipboard.paste():
            pass # wait till user copied knew URL
        url = clipboard.paste()
        print(url)
        cur_obj["URL"] = url

        c = input("Ratings: [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER [S]kip [Q]uit\n")
        if c in ['1', '2', '3', '4', '5', '6', '7']:
            cur_obj["Category"] = c
        elif c in ['s', 'S']:
            continue
        elif c in ['q', 'Q']:
            return

        cur_obj = download_fields(cur_obj)
        RESULTS.append(cur_obj)
        save()

'''
Function for adding the downloaded fields
for classified JSON data with only URL and Category
'''
def extend_fields(in_file):
    RESULTS = json.load(open(in_file, "r"))
    # download fields for each object
    i=0
    for obj in RESULTS:
        RESULTS[i] = download_fields(obj)
        i += 1
        save() # indent out

if __name__ == '__main__':
    extend_fields("./classification/classified.json")
