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
from datetime import datetime

import pymongo
from abc import abstractmethod

from pymongo.database import Database

from mongo_migrate.config import Config


class BaseMigration(object):
    def __init__(self, config: Config):
        client = pymongo.MongoClient(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            authSource="admin"
        )
        self.db: Database = client[config.database]

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

    def add_timestamps(self, doc: dict, created: bool) -> dict:
        """
        Add created/updated at timestamps to given document.
        """
        ret = doc.copy()

        now = datetime.now()
        time_keys = ["updated"]
        if created:
            time_keys.append("created")

        for key in time_keys:
            ret[f"{key}_at"] = now

        return ret