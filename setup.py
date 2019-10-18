# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='GithubClassifier',
    author='Maxim Schuwalow, Fabian Richter, Tobias Ludwig',
    author_email='mschuwalow@uos.de',
    packages=['classification'],
    install_requires=["beautifulsoup4 == 4.5.3",
                    'boto==2.45.0',
                    'bs4==0.0.1',
                    'bson==0.4.3',
                    'bz2file==0.98',
                    'clipboard==0.0.4',
                    'gensim==0.13.4.1',
                    'github3.py==0.9.6',
                    'Markdown==2.6.7',
                    'numpy==1.11.3',
                    'protobuf==3.0.0',
                    'pymongo==3.4.0',
                    'pyperclip==1.5.27',
                    'pytz==2016.10',
                    'requests==2.12.4',
                    'simplejson==3.10.0',
                    'six==1.10.0',
                    'smart-open==1.3.5',
                    'uritemplate==3.0.0',
                    'uritemplate.py==3.0.2',
                    # 'tensorflow == 0.12.1', not in pip for ubuntu
                    'more-itertools==2.5.0',
                    'flask==1.0',
                    'flask-cors==3.0.2',
                    'urllib3==1.19.1'
    ],
    zip_safe=False,
    entry_points={
       "console_scripts": [
           "github-classify=classification.eval:start_eval_server",
       ],
    },
)
