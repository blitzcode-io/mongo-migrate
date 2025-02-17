"""
    Module: base_migrate.py
    Author: Rahul George
    
    Description:
        This module will act as the base class for all the migration files.
        It will take care of the database connection.
        The child classes should worry about implementing the actual migration.
    License:
    
    Created on: 15-08-2023
    
"""
import pymongo
from abc import abstractmethod


class BaseMigration(object):
    def __init__(self, config):
        # URI and host+port support
        if config.uri is not None:
            mongo_uri = f"mongodb+srv://{config.uri}"
        else:
            mongo_uri = f"mongodb://{config.host}:{config.port}"

        client = pymongo.MongoClient(mongo_uri)
        self.db = client[config.database]

    @abstractmethod
    def upgrade(self):
        """Implement this in the child classes"""
        pass

    @abstractmethod
    def downgrade(self):
        """Implement this in the child classes"""
        pass

    @abstractmethod
    def comment(self):
        """Implement this in the child classes"""
        pass

