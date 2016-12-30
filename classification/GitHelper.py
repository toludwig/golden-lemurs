#!/usr/bin/python3

from github3 import login
from github3.null import NullObject
from markdown import markdown
from bs4 import BeautifulSoup
from random import randint

tokens = [login(token='9e484681cd48b198297bb0de032445f92a962282'),
          login(token='360e0d54fe6c4e1e944bcb6c2ed0533389683758'),
          login(token='16bf3237e831bbb0a226eeae44313ca2254f49be'),
          login(token='d357de7b1afbf063489f189f4afae3b678c48aeb'),
          login(token='562373b01a5538554be70cd9da1cab100e70f34c'),
          login(token='1b661528ad9c44d9e93aa3d1c6cee8a9c76ab984'),
          login(token='7ca977da54b4ca3b3704c7d52a76188ccbe1e371'),
          login(token='85d168fcb6f40e92026cf29050b03391a888c340'),
          login(token='c245bd72e2408680e9e8136b162e45df022a1ed8')]


def _token():
    i = randint(0, len(tokens) - 1)
    return tokens[i]


class Git():
    """docstring for Git."""

    def __init__(self, user, title):
        self.api = _token()
        # repo may not exist
        self.repo = self.api.repository(user, title)

    def valid(self):
        return (False if self.repo is None else True)

    def is_fork(self):
        return self.repo.fork

    def number_contributors(self):
        return len(list(self.repo.iter_contributors()))

    def get_readme(self):
        readme = self.repo.readme()
        if not type(readme) == NullObject:
            text = BeautifulSoup(readme.decoded, "html.parser").text
            return text
        return ''

    def number_commits(self):
        return len(list(self.repo.iter_commits()))

    def number_issues(self):
        return len(list(self.repo.iter_issues()))

    def number_branches(self):
        try:
            return len(list(self.repo.branches()))
        except:
            return 1

    def number_forks(self):
        try:
            return len(list(self.repo.forks()))
        except:
            return 1

    def number_pull_requests(self):
        return len(list(self.repo.iter_pulls(state='all')))

    def number_stars(self):
        return len(list(self.repo.iter_stargazers()))

    def number_subscribers(self):
        return len(list(self.repo.iter_subscribers()))

    def get_commit_times(self):
        repo = list(self.repo.iter_commits())
        return list(map(lambda x: x.commit.author['date'], repo))

    def get_commits(self):
        repo = list(self.repo.iter_commits())
        return list(map(lambda x: x.commit.message, repo))

    def get_issues(self):
        repo = list(self.repo.iter_issues())
        return list(map(lambda x: list(map(lambda y: y.body_text
                                           , x.iter_comments()))
                        , repo))

    def get_times(self):
        created = self.repo.created_at.timestamp()
        last = self.repo.updated_at.timestamp()
        return (created, last)
