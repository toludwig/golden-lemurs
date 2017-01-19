#!/usr/bin/python3
"""
Wrapper around the github api. The functionality is tested, but all functions in this class will just pass any Exceptions
they encounter up from the github3 api.
"""
from github3 import login
from bs4 import BeautifulSoup
from random import randint
import requests
import json
import urllib3
import logging
import inspect
import time
from more_itertools import ilen

logger = logging.getLogger(__name__)

# keys = ['9e484681cd48b198297bb0de032445f92a962282',
#         '360e0d54fe6c4e1e944bcb6c2ed0533389683758',
#         '16bf3237e831bbb0a226eeae44313ca2254f49be',
#         'd357de7b1afbf063489f189f4afae3b678c48aeb',
#         '562373b01a5538554be70cd9da1cab100e70f34c',
#         '1b661528ad9c44d9e93aa3d1c6cee8a9c76ab984',
#         '7ca977da54b4ca3b3704c7d52a76188ccbe1e371',
#         '85d168fcb6f40e92026cf29050b03391a888c340',
#         'c245bd72e2408680e9e8136b162e45df022a1ed8']
keys = ['cd98286d44c5094cac34caed538ad438f937cb4f']


# $issueLimit: Int!

# issues
#   pageInfo {
#     endCursor
#     hasNextPage
#     startCursor
#     hasPreviousPage
#   }
#   nodes {
#     title
#     createdAt
#   }
query = """query RepoInfo($owner: String!, $name: String!, $commitLimit: Int!) {
  repository(owner: $owner, name: $name) {
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
    mentionableUsers {
      totalCount
    }
    issues {
      totalCount
    }
    commits: ref(qualifiedName: "master") {
      target {
        ... on Commit {
          tree {
            oid
          }
          history(first: $commitLimit) {
            pageInfo {
                endCursor
                hasNextPage
                startCursor
                hasPreviousPage
            }
            edges {
              node {
                message
                author {
                  date
                }
              }
            }
          }
        }
      }
    }
  }
}"""

stream_issues = """query Issues($owner: String!, $name: String!, $issueLimit: Int!, $issueCursor: String!) {
  repository(owner:$owner, name: $name) {
    issues(after: $issueCursor first: $issueLimit) {
      pageInfo {
        endCursor
        hasNextPage
        startCursor
        hasPreviousPage
      }
      edges {
        node {
          title
        }
      }
    }
  }
}"""

stream_commits = """
query Commits($owner: String!, $name: String!, $commitLimit: Int!, $commitCursor: String!) {
  repository(owner:$owner, name: $name) {

     commits: ref(qualifiedName: "master") {
      target {
        ... on Commit {
          tree {
            oid
          }
          history(after: $commitCursor first: $commitLimit) {
            pageInfo {
              hasNextPage
              endCursor
              startCursor
              hasPreviousPage
            }
            edges {
              node {
                message
                author {
                  date
                }
              }
            }
          }
        }
      }
    }
  }
}"""

tokens = list(map(lambda key: login(token=key), keys))

http = urllib3.PoolManager()


def _fallback(fallback):
    def decorator(function):
        def f(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
                return result
            except Exception:
                result = fallback(*args, **kwargs)
                return result
        return f
    return decorator


def class_decorator(cls):
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        setattr(cls, name, _retry_deco(method, 300))
    return cls


def _retry_deco(function, delta):
    def f(self, *args, **kwargs):
        try:
            timeout = getattr(self, 'timeout')
        except Exception:
            timeout = time.time() + delta
            setattr(self, 'timeout', timeout)
        while True:
            if time.time() > timeout:
                logger.exception("Timeout while executing %s" % function.__name__)
                raise TimeoutError
            try:
                result = function(self, *args, **kwargs)
                return result
            except Exception as err:
                logger.info('Exception in %s: %s' % (function.__name__, err))
                time.sleep(5)
    return f


def get_all(user, title):
    repo = {}
    git = Git(user, title)
    if not git.valid():
        return None
    repo["User"] = user
    repo["Title"] = title
    repo["Readme"] = git.get_readme()
    repo["NumberOfContributors"] = git.number_contributors()
    repo["Branches"] = git.number_branches()
    repo["Forks"] = git.number_forks()
    repo["Stars"] = git.number_stars()
    repo["Pulls"] = git.number_pull_requests()
    repo["Subscribers"] = git.number_subscribers()
    repo["NumberOfCommits"], repo["CommitTimes"], repo["CommitMessages"] = git.get_commits()
    repo["Times"] = git.get_times()
    repo["Files"] = git.get_files()
    return repo


def _graphql(api, data, token):
    encoded_data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json',
               'Authorization': 'bearer %s' % token, 'User-Agent': 'crawler'}
    req = http.request('POST', api, body=encoded_data, headers=headers)
    res = json.loads(req.data.decode('utf-8'))
    return res


@_fallback(get_all)
def fetch_repo(user, name, commit_limit=-1): #, issue_limit=-1):
    api = 'https://api.github.com/graphql'
    MAX_FIRST = 100

    request = {}
    request['operationName'] = "RepoInfo"
    request['query'] = query
    c_lim = MAX_FIRST if commit_limit == -1 else min(commit_limit, MAX_FIRST)
    # i_lim = MAX_FIRST if issue_limit == -1 else min(issue_limit, MAX_FIRST)
    request['variables'] = json.dumps( {"owner": user, "name": name, "commitLimit": c_lim}) #, "issueLimit": i_lim})

    response = _graphql(api, request, _token(as_key=True))
    print(response)

    result = response['data']['repository']
    repo = {}
    repo['User'] = user
    repo['Title'] = name
    repo['Stars'] = result['stargazers']['totalCount']
    repo['Pulls'] = result['pullRequests']['totalCount']
    repo['Forks'] = result['forks']['totalCount']
    repo['Subscribers'] = result['watchers']['totalCount']
    repo['NumberOfContributors'] = result['mentionableUsers']['totalCount']
    repo['Times'] = result['createdAt'], result['updatedAt']
    #issues = result['issues']['nodes']
    repo['NumberOfIssues'] = result['issues']['totalCount']
    commits = result['commits']['target']['history']['edges']
    sha = result['commits']['target']['tree']['oid']

    # paginated content
    remaining_commits = 0
    # remaining_issues = 0
    # first_query = result

    def commits_left():
        nonlocal remaining_commits
        if commit_limit == -1:
            remaining_commits = MAX_FIRST
        else:
            remaining_commits = commit_limit - len(commits)
        return remaining_commits > 0 and c_cursor is not None and result['commits']['target']['history']['pageInfo']['hasNextPage']
    #
    # def issues_left():
    #     nonlocal remaining_issues
    #     if issue_limit == -1:
    #         remaining_issues = MAX_FIRST
    #     else:
    #         remaining_issues = issue_limit - len(issues)
    #     return remaining_issues > 0 and i_cursor is not None and result['issues']['pageInfo']['hasNextPage']

    c_cursor = result['commits']['target']['history']['pageInfo']['endCursor']
    # i_cursor = result['issues']['pageInfo']['endCursor']

    while commits_left():
        request = {}
        request['operationName'] = "Commits"
        request['query'] = stream_commits
        request['variables'] = json.dumps({
            "owner": user, "name": name,
            "commitLimit": min(remaining_commits, MAX_FIRST),
            "commitCursor": c_cursor})

        response = _graphql(api, request, _token(as_key=True))
        result = response['data']['repository']
        commits += result['commits']['target']['history']['edges']
        c_cursor = result['commits']['target']['history']['pageInfo']['endCursor']

    # result = first_query
    #
    # while issues_left():
    #     request = {}
    #     request['operationName'] = "Issues"
    #     request['query'] = stream_issues
    #     request['variables'] = json.dumps({
    #         "owner": user, "name": name,
    #         "issueLimit": min(remaining_issues, MAX_FIRST),
    #         "issueCursor": i_cursor})
    #
    #     response = _graphql(api, request, _token(as_key=True))
    #     result = response['data']['repository']
    #     if 'nodes' in result['issues']:
    #         issues += result['issues']['nodes']
    #     i_cursor = result['issues']['pageInfo']['endCursor']


    repo['CommitTimes'] = list(
        map(lambda c: c['node']['author']['date'], commits))
    repo['CommitMessages'] = list(map(lambda c: c['node']['message'], commits))
    repo['NumberOfCommits'] = len(commits)

    # repo['IssueTimes'] = list(map(lambda i: i['createdAt'], issues))
    # repo['IssueMessages'] = list(map(lambda i: i['title'], issues))

    # fetch remaining content
    git = Git(user, name)
    repo["Readme"] = git.get_readme()
    repo["Files"] = git.get_files(id=sha)

    return repo


selected_token = randint(0, len(tokens) - 1)


def _token(as_key=False):
    global selected_token
    if tokens[selected_token].rate_limit()['resources']['core']['remaining'] > 0:
        return tokens[selected_token] if not as_key else keys[selected_token]
    else:
        selected_token = None
        while selected_token is None:
            selected_token = randint(0, len(tokens) - 1)
            if not tokens[selected_token].rate_limit()['resources']['core']['remaining'] > 0:
                selected_token = None
        return tokens[selected_token] if not as_key else keys[selected_token]


def _commit_info(commit):

    return commit.commit.author["date"], commit.commit.message


@class_decorator
class Git:
    """docstring for Git."""
    def __init__(self, user, title):
        self.api = _token()
        self.user = user
        self.title = title
        self.repo = self.api.repository(user, title)
        logger.info('crawling %s/%s' % (user, title))

    def valid(self):
        return False if self.repo is None else True

    def is_fork(self):
        return self.repo.fork

    def number_contributors(self):
        return ilen(self.repo.iter_contributors())

    def get_readme(self):
        readme = self.repo.readme()
        if readme is not None:
            text = BeautifulSoup(readme.decoded, "html.parser").text
            return text
        return ''

    def number_issues(self):
        return ilen(self.repo.iter_issues())

    def number_branches(self):
        try:
            return ilen(self.repo.branches())
        except AttributeError:
            logger.info('No branches found. returning 0')
            return 0

    def number_forks(self):
        try:
            return ilen(self.repo.iter_forks())
        except AttributeError:
            logger.info('No forks found. returning 0')
            return 0

    def number_pull_requests(self):
        return ilen(self.repo.iter_pulls(state='all'))

    def number_stars(self):
        return len(list(self.repo.iter_stargazers()))

    def number_subscribers(self):
        return len(list(self.repo.iter_subscribers()))

    def get_commits(self, limit=400):
        repo = list(self.repo.iter_commits())
        temp = list(map(lambda x: _commit_info(x), repo))[:limit]
        return len(repo), [commit[0] for commit in temp], [commit[1] for commit in temp]

    def get_issues(self):
        repo = list(self.repo.iter_issues())
        return list(map(lambda x: list(map(lambda y: y.body_text, x.iter_comments())), repo))

    def get_times(self):
        created = self.repo.created_at.timestamp()
        last = self.repo.updated_at.timestamp()
        return created, last

    def get_files(self, id=None):
        header = {'Authorization': 'token %s' % _token(as_key=True)}
        api = 'https://api.github.com/repos/%s/%s' % (self.user, self.title)
        if id is None:
            commits = requests.get('%s/commits' % api, headers=header)
            id = commits.json()[0]['sha']
        tree = requests.get('%s/git/trees/%s' % (api, id), params={'recursive': '1'}, headers=header)
        names = list(map(lambda entry: entry['path'], tree.json()['tree']))
        return names