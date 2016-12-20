from pymongo import MongoClient

DB_URI = "mongodb://Flask:ksalf@ds052629.mlab.com:52629/storage"

db = MongoClient(DB_URI).storage

TELEGRAM_API = "260971496:AAHz1sy54uDLOI7o34DxJQTT8Uzp5TWJORw"
TELEGRAM_TARGETS = [-192529818]
