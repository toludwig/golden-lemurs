import bson
from . import db


class Logger(object):
    """
    Stores neural network data in a database for later comparison.
    Provide the name, description and entire relevant source code as a
    string during initialization.
    """
    def __init__(self, name, description):
        super(Logger, self).__init__()
        self.id = bson.ObjectId(db.networks.insert({'name': name,
                                                    'description': description}))

    def set_source(self, source):
        db.source.update({'_id': self.id}, {'$set': {"source": source}})

    def set_training_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"accuracy": accuracy}})

    def set_test_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"test_accuracy": accuracy}})

    def set_cost(self, cost):
        db.networks.update({'_id': self.id}, {'$set': {"cost": cost}})
