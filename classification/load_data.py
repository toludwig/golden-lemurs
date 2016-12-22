from .GitHelper import Git
import json

def _load(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        print('no data found; creating %s' % file)
        return []

def _save(data, file):
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4 * " ")

def load_data(repos, results, category):
    data = _load(results)
    with open(repos, 'r') as file:
        urls = json.load(file)
        for url in urls:
            repo = download_fields(url)
            repo["Category"] = category
            data.append(repo)
    _save(data, results)

def _options():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="out", action="store",
                      type="string", default='./results.json', help="file with results")
    parser.add_option("-r", "--repos", dest="list", action="store",
                      type="string", default='./list.json', help="file with repo urls")
    parser.add_option("-c", "--category", dest="category", action="store", type="string", default='7', help="category to assign")

    return parser.parse_args()

def main():
    (options, args) = _options()
    load_data(options.list, options.out, options.category)

if __name__ == '__main__':
    main()
