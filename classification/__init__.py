import os
# from pymongo import MongoClient

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'out'))

# DB_URI = ""
# db = MongoClient(DB_URI).storage
