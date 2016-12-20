from pymongo import MongoClient

DB_URI = "mongodb://Flask:ksalf@ds052629.mlab.com:52629/storage"

db = MongoClient(DB_URI).storage
