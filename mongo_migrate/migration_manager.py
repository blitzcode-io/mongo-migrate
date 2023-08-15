"""
    Module: migration_manager.py
    Author: Rahul George
    
    Description:
    This is the core of the mongo_migrate library.
    
    License:
    
    Created on: 14-08-2023
    
"""
import os.path
import sys
from datetime import datetime
from importlib import import_module
from string import Template

from mongo_migrate.exceptions import MongoMigrateException
from mongo_migrate.base_migrate import BaseMigration


class MigrationManager(object):

    NEW_MIGRATION_STRING = Template("""
from mongo_migrate.base_migrate import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        pass
        
    def downgrade(self):
        pass
        
    def comment(self):
        return '$comment'
    """)

    def __init__(self, config, migrations_path):
        self.config = config        # database config - host, port, db
        self.migrations_path = migrations_path
        self.db = None

    def migrate(self, direction, upto):
        """Public method to perform the migration - upgrade or downgrade"""
        # identify the specific migrations

        if not os.path.exists(self.migrations_path):
            raise MongoMigrateException('Cannot find the migrations path: {}'.format(self.migrations_path))

        all_migrations = os.listdir(self.migrations_path)
        all_migrations_timestamp = list(map(self.timestamp_from_filename, all_migrations))

        migrate_instance = BaseMigration(self.config)
        self.db = migrate_instance.db

        if direction == 'upgrade':
            self._do_upgrade(all_migrations, all_migrations_timestamp, upto)
        else:
            self._do_downgrade(all_migrations, all_migrations_timestamp, upto)

        # identify the starting point to migrate from. [Need connection to DB]
        # Identify the specific migrations to pick to reach the target migration.
        # Initialize, iterate over the specific migrations and call the appropriate method.
        # After each iteration, print the file name.

        pass

    def create_migration(self, title, message):
        """Create the folder and the template migration file."""
        if not os.path.exists(self.migrations_path):
            os.makedirs(self.migrations_path)

        filename = "{}/{}_{}.py".format(
            self.migrations_path,
            datetime.now().strftime('%Y%m%d%H%M%S'),
            title)

        with open(filename, 'w') as fh:
            fh.write(self.NEW_MIGRATION_STRING.safe_substitute(comment=message))

        print('Migration file created: {}'.format(filename))

    def _do_upgrade(self, all_migrations, all_migration_timestamps, target_migration):
        # check collection exists
        # check if any past migrations exists,
        # if yes, take the last migration as the start
        # get the migrations to apply.
        # Iteratively apply.

        if not self._get_migration_history_collection():
            self.db.create_collection('migration_history')

        past_migrations = self._get_migration_history()
        if len(past_migrations):
            start_datetime = past_migrations[-1]['migration_datetime']
            start_idx = all_migration_timestamps.index(start_datetime) + 1
        else:
            start_idx = 0

        last_idx = all_migration_timestamps.index(target_migration)
        migrations_to_apply = all_migrations[start_idx: last_idx+1]

        if not migrations_to_apply:
            print("No new changes to apply")
            return

        # Perform migration by executing the upgrade method from the identified migrations
        sys.path.append(self.migrations_path)
        for migration in migrations_to_apply:
            migration_module = import_module(migration[:-3])
            migration_instance = migration_module.Migration(self.config)
            migration_instance.upgrade()

            self._create_migration_milestone(migration[0:14])

            print("Applied migration: '{}'".format(migration))

    def _do_downgrade(self, all_migrations, all_migration_timestamps, target_migration):
        pass

    def _get_migration_history_collection(self):
        return self.db.list_collection_names(filter={'name': 'migration_history'})

    def _get_migration_history(self, db_filter=None):
        if db_filter is None:
            db_filter = {}
        return list(self.db.migration_history.find(db_filter))

    @classmethod
    def timestamp_from_filename(cls, filename):
        return filename.split('_')[0]

    def _create_migration_milestone(self, migration_datetime):
        self.db.migration_history.insert_one({'migration_datetime': migration_datetime,
                                              'created_on': datetime.now()})

    def _delete_migration_milestone(self, migration_datetime):
        self.db.migration_history.delete_one({'migration_date_time': migration_datetime})

