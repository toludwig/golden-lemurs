import bson
from . import db


class Logger:
    """
    Stores neural network data in a database for later comparison.
    Provide the name, description and entire relevant source code as a
    string during initialization.
    """
    def __init__(self, name, description=''):
        super(Logger, self).__init__()
        self.id = bson.ObjectId(db.networks.insert({'name': name}))
        db.source.insert({'_id': self.id})
        self.set_cost([0])
        self.set_training_acc([0])
        self.set_test_acc([0])
        self.set_score(0)
        self.set_description(description)

    def set_description(self, description):
        db.networks.update({'_id': self.id}, {'$set': {'description': description}})

    def set_source(self, source_file):
        with open(source_file, 'r') as file:
            source = file.read()
        db.source.update({'_id': self.id}, {'$set': {"source": source}})

    def set_training_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"accuracy": accuracy}})

    def set_test_acc(self, accuracy):
        db.networks.update({'_id': self.id}, {'$set': {"test_accuracy": accuracy}})

    def set_cost(self, cost):
        db.networks.update({'_id': self.id}, {'$set': {"cost": cost}})

    def set_score(self, score):
        db.networks.update({'_id': self.id}, {'$set': {"score": score}})
