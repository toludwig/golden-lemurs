#!/usr/bin/python3

from github3 import login
from markdown import markdown
from bs4 import BeautifulSoup
from random import randint

def _token():
    tokens = ['9e484681cd48b198297bb0de032445f92a962282', '360e0d54fe6c4e1e944bcb6c2ed0533389683758']
    i = randint(0, len(tokens) - 1)
    return tokens[i]

class Git(object):
    """docstring for Git."""

    def __init__(self, user, title):
        super(Git, self).__init__()
        self.api = login(token=_token())
        # repo may not exist
        self.repo = None
        try:
            self.repo = self._get_repo(user, title)
            self.valid = True
        except StopIteration:
            self.valid = False

    def _get_repo(self, user, title):
        return self.api.search_repositories('%s user:%s fork:true' % (title, user)).next().repository

    def number_contributors(self):
        return len(list(self.repo.iter_contributors()))

    def get_readme(self):
        readme = self.repo.readme()
        if(readme is not None):
            text = BeautifulSoup(readme.decoded, "html.parser").text
            return text
        return ''

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
