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
    title = split[3]
    user = split[4]
    return (user, title)

def save():
    print(RESULTS)
    with open(OUT_FILE, "w") as f:
        json.dump(RESULTS, f)

def download_additional_fields():
    user, title = split_url(CUR_OBJ["URL"])
    readme = Git().get_readme(user, title)
    CUR_OBJ["User"] = user
    CUR_OBJ["Title"] = title
    CUR_OBJ["Readme"] = readme

def main():
    global CUR_OBJ
    options()
    url = ""

    while True:
        CUR_OBJ={}

        print("\nURL: ")
        while url == clipboard.paste():
            pass # wait till user copied knew URL
        url = clipboard.paste()
        print(url)
        CUR_OBJ["URL"] = url

        c = input("Ratings: [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER [S]kip [Q]uit\n")
        if c in ['1', '2', '3', '4', '5', '6', '7']:
            CUR_OBJ["Category"] = c
        elif c in ['s', 'S']:
            continue
        elif c in ['q', 'Q']:
            break

        download_additional_fields()
        RESULTS.append(CUR_OBJ)

        save()

if __name__ == '__main__':
    main()
