import os
import sys
# from pymongo import MongoClient
import logging
import logging.config
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'out'))
TOKENS = [
# INSERT GITHUB PERSONAL ACCESS TOKENS HERE
# NECESSARY ACCESS RIGHTS: repo (full control of private repositories)
# NEEDED FOR: GraphQL API & REST API
]

# DB_URI = ""
# db = MongoClient(DB_URI).storage
