#!/usr/bin/python3
import sys
import json
import clipboard
from optparse import OptionParser
import "GitHelper.py"

OUT_FILE="results.json"
RESULTS=[]
CUR_OBJ={}

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

def download_additional_fields():
    readme = 
    # CUR_OBJ["Readme"] = readme
    pass

def main():
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
