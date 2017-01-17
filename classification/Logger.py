import bson
# from . import db
import inspect
"""
Logger that logs into a remote MongoDB. Disabled for submission
"""

class Logger:
    """
    Stores neural network data in a database for later comparison.
    """
    def __init__(self, name, description=''):
        # self.id = bson.ObjectId(db.networks.insert({'name': name}))
        # db.source.insert({'_id': self.id})
        # self.set_cost([0])
        # self.set_training_acc([0])
        # self.set_test_acc([0])
        # self.set_score(0)
        # self.set_description(description)
        # self.set_source_string("")
        pass

    def set_description(self, description):
        # db.networks.update({'_id': self.id}, {'$set': {'description': description}})
        pass

    def set_source(self, c):
        # source_file = inspect.getfile(c.__class__)
        #
        # with open(source_file, 'r') as file:
        #     source = file.read()
        # db.source.update({'_id': self.id}, {'$set': {"source": source}})
        pass

    def set_source_string(self, source):
        # db.source.update({'_id': self.id}, {'$set': {"source": source}})
        pass

    def set_training_acc(self, accuracy):
        # db.networks.update({'_id': self.id}, {'$set': {"accuracy": accuracy}})
        pass

    def set_test_acc(self, accuracy):
        # db.networks.update({'_id': self.id}, {'$set': {"test_accuracy": accuracy}})
        pass

    def set_cost(self, cost):
        # db.networks.update({'_id': self.id}, {'$set': {"cost": cost}})
        pass

    def set_score(self, score):
        # db.networks.update({'_id': self.id}, {'$set': {"score": score}})
        pass
