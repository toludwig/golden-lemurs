from pymongo import MongoClient
import simplejson as json
import bson
from . import db

class Logger(object):
    """
    Stores neural network data in a database for later comparison.
    Provide the name, description and entire relevant source code as a
    string during initialization.
    """
    def __init__(self, name, description, source_code):
        super(Logger, self).__init__()
        self.id = bson.ObjectId(db.source.insert({'source': source_code}))
        db.networks.insert_one({'_id': self.id, 'name': name, 'description': description})

    def set_training_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"accuracy": accuracy}})

    def set_test_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"test_accuracy": accuracy}})

    def set_cost(self, cost):
        db.networks.update({'_id': self.id}, {'$set': {"cost": cost}})
