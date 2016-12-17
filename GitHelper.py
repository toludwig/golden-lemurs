from github3 import login
from markdown import markdown
from bs4 import BeautifulSoup

GITHUB_TOKEN = '9e484681cd48b198297bb0de032445f92a962282'

def split_url(url):
    split = url.split('/')
    title = split[-1]
    user = split[-2]
    return (user, title)

class Git(object):
    """docstring for Git."""
    def __init__(self):
        super(Git, self).__init__()
        self.api = login(token=GITHUB_TOKEN)


    def get_readme(self, user, title):
        repo = self.api.search_repositories('%s user:%s fork:true' \
                                            % (title, user)).next().repository
        readme = repo.readme().decoded
        text = BeautifulSoup(readme, "html.parser")
        return text
