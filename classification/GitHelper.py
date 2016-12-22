#!/usr/bin/python3

from github3 import login
from github3.null import NullObject
from markdown import markdown
from bs4 import BeautifulSoup
from random import randint

def _token():
    tokens = ['9e484681cd48b198297bb0de032445f92a962282',
              '360e0d54fe6c4e1e944bcb6c2ed0533389683758']
    i = randint(0, len(tokens) - 1)
    return tokens[i]


class Git(object):
    """docstring for Git."""

    def __init__(self, user, title):
        super(Git, self).__init__()
        self.api = login(token=_token())
        # repo may not exist
        self.repo = self.api.repository(user, title)
        self.valid = not type(self.repo) == NullObject

    def number_contributors(self):
        return len(list(self.repo.contributors()))

    def get_readme(self):
        readme = self.repo.readme()
        if not type(readme) == NullObject:
            text = BeautifulSoup(readme.decoded, "html.parser").text
            return text
        return ''

    def get_commits(self):
        commits = list(self.repo.commits())
        return list(map(lambda x: x.message, commits))

    def get_issues(self):
        issues = list(self.repo.issues())
        titles = list(map(lambda issue: issue.title, issues))
        comments = list(map(lambda issue: list(map(
            lambda comment: comment.body_text, issue.comments())),
            issues))

        i = 0
        for i in range(len(titles)):
            comments[i].insert(0, titles[i])
        return comments

    def get_times(self):
        created = self.repo.created_at.timestamp()
        last = self.repo.updated_at.timestamp()
        return (created, last)
