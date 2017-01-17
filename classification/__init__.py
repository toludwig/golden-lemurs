import os
import sys
# from pymongo import MongoClient
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'out'))

# DB_URI = ""
# db = MongoClient(DB_URI).storage
