#!/usr/bin/python3

from github3 import login
from markdown import markdown
from bs4 import BeautifulSoup

GITHUB_TOKEN = '9e484681cd48b198297bb0de032445f92a962282'

class Git(object):
    """docstring for Git."""

    def __init__(self, user, title):
        super(Git, self).__init__()
        self.api = login(token=GITHUB_TOKEN)
        self.repo = self._get_repo(user, title)

    def _get_repo(self, user, title):
        repo = self.api.search_repositories('%s user:%s fork:true'
                                            % (title, user)).next().repository
        return repo

    def number_contributors(self):
        return len(list(self.repo.iter_contributors()))

    def get_readme(self):
        if(readme = self.repo.readme().decoded is not None):
            text = BeautifulSoup(readme, "html.parser").text
            return text
        return ''

    def number_commits(self):
        return len(list(self.repo.iter_commits()))

    def get_commits(self):
        repo = list(self.repo.iter_commits())
        return list(map(lambda x: x.commit.message, repo))

    def number_issues(self):
        return len(list(self.repo.iter_issues()))

    def get_issues(self):
        repo = list(self.repo.iter_issues())
        return list(map(lambda x: list(map(lambda y: y.body_text
                                           , x.iter_comments()))
                        , repo))

    def get_times(self):
        created = self.repo.created_at
        last = self.repo.updated_at
        return (created, last)
