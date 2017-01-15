#!/usr/bin/python3

from github3 import login
from markdown import markdown
from bs4 import BeautifulSoup
from random import randint
import requests

# keys = ['9e484681cd48b198297bb0de032445f92a962282']

keys = ['9e484681cd48b198297bb0de032445f92a962282',
 '360e0d54fe6c4e1e944bcb6c2ed0533389683758',
 '16bf3237e831bbb0a226eeae44313ca2254f49be',
 'd357de7b1afbf063489f189f4afae3b678c48aeb',
 '562373b01a5538554be70cd9da1cab100e70f34c',
 '1b661528ad9c44d9e93aa3d1c6cee8a9c76ab984',
 '7ca977da54b4ca3b3704c7d52a76188ccbe1e371',
 '85d168fcb6f40e92026cf29050b03391a888c340',
 'c245bd72e2408680e9e8136b162e45df022a1ed8']


tokens = list(map(lambda key: login(token=key), keys))

# Type queries into this side of the screen, and you will
# see intelligent typeaheads aware of the current GraphQL type schema,
# live syntax, and validation errors highlighted within the text.

# We'll get you started with a simple query showing your username!
graph_ql_query = """query RepoInfo($owner:String!, $name:String!) {
    repository(owner:$owner, name: $name) {
    	isFork
      updatedAt
      createdAt
      stargazers {
        totalCount
      }
      pullRequests {
        totalCount
      }
      forks {
        totalCount
      }
      watchers {
        totalCount
      }
    }
  }
  """

selected_token = randint(0, len(tokens) - 1)

def _token(as_key=False):
    global selected_token
    if tokens[selected_token].rate_limit()['resources']['core']['remaining'] > 0:
        return (tokens[selected_token] if not as_key else keys[selected_token])
    else:
        selected_token = None
        while selected_token is None:
            selected_token = randint(0, len(tokens) - 1)
            if not tokens[selected_token].rate_limit()['resources']['core']['remaining'] > 0:
                selected_token = None
        return (tokens[selected_token] if not as_key else keys[selected_token])


def _commit_info(commit):
    return commit.author["date"], commit.message


class Git:
    """docstring for Git."""

    def __init__(self, user, title):
        self.api = _token()
        self.user = user
        self.title = title
        # repo may not exist
        self.repo = self.api.repository(user, title)

    def valid(self):
        return False if self.repo is None else True

    def is_fork(self):
        return self.repo.fork

    def number_contributors(self):
        return len(list(self.repo.iter_contributors()))

    def get_readme(self):
        readme = self.repo.readme()
        if readme is not None:
            text = BeautifulSoup(readme.decoded, "html.parser").text
            return text
        return ''

    def number_issues(self):
        return len(list(self.repo.iter_issues()))

    def number_branches(self):
        try:
            return len(list(self.repo.branches()))
        except Exception:
            return 1

    def number_forks(self):
        try:
            return len(list(self.repo.forks()))
        except Exception:
            return 1

    def number_pull_requests(self):
        return len(list(self.repo.iter_pulls(state='all')))

    def number_stars(self):
        return len(list(self.repo.iter_stargazers()))

    def number_subscribers(self):
        return len(list(self.repo.iter_subscribers()))

    def get_commits(self):
        repo = list(self.repo.iter_commits())
        return len(repo), list(map(lambda x: _commit_info(x), repo))

    def get_issues(self):
        repo = list(self.repo.iter_issues())
        return list(map(lambda x: list(map(lambda y: y.body_text
                                           , x.iter_comments()))
                        , repo))

    def get_times(self):
        created = self.repo.created_at.timestamp()
        last = self.repo.updated_at.timestamp()
        return created, last

    def get_files(self):
        debug = {}
        try:
            header = { 'Authorization': 'token %s' % _token(as_key=True)}
            api = 'https://api.github.com/repos/%s/%s' % (self.user, self.title)
            commits = requests.get('%s/commits' % api,
                headers=header)
            debug['commits'] = commits.json()
            sha = commits.json()[0]['sha']
            tree = requests.get('%s/git/trees/%s' % (api, sha), params={'recursive': '1'}, headers=header)
            debug['tree'] = tree.json()
            names = list(map(lambda entry: entry['path'], tree.json()['tree']))
            return names
        except Exception as e:
            print(e)
            print(debug)
            raise e
