"""
    Module: migration_manager.py
    Author: Rahul George
    
    Description:
    This is the core of the mongo_migrate library.
    
    License:
    
    Created on: 14-08-2023
    
"""
import os.path
import re
import sys
from datetime import datetime
from importlib import import_module
from string import Template


import pymongo
from pymongo.database import Database

from mongo_migrate.enums import BaseFlag, Direction, DirectionTargetOptions
from mongo_migrate.exceptions import MongoMigrateException
from mongo_migrate.base_migrate import BaseMigration
from mongo_migrate.migration_walker import MigrationWalker
from mongo_migrate.config import Config
from mongo_migrate.utils import direction_target_is_valid, is_keyword_target

class MigrationManager(object):

    NEW_MIGRATION_STRING = Template("""from mongo_migrate.base_migrate import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        pass
        
    def downgrade(self):
        pass
        
    def comment(self):
        return '$comment'
    """)

    def __init__(self, config: Config, migrations_path: str):
        self.config = config
        self.migrations_path = migrations_path

        migrate_instance = BaseMigration(self.config)
        self.db: Database = migrate_instance.db

    def get_migration_walker(self) -> MigrationWalker:
        """
        Get migration walker based on currently present migrations.

        Get list of all migrations at moment of calling this method.
        Create migration walker based on those migrations.
        """
        all_migrations = self.get_all_migrations()
        ret = MigrationWalker(all_migrations)
        return ret
 
    def get_all_migrations(self) -> list[str]:
        """
        Get list of all migration filenames from oldest to newest.
        """
        ret = list(filter(lambda x: re.match('\d+_.+\.py', x), os.listdir(self.migrations_path)))
        ret.sort()
        return ret

    def migrate(self, direction: Direction, target: str):
        """
        Public method to perform the migration - upgrade or downgrade

        target options: timestamp or keyword target (head/base or +N/-N)

        Check validity of requested operation (compatibility between direction and target).
        Determine target migration timestamp if not given explicitly (e.g. upgrade head)
        Full downgrade to base means timestamp None to trigger downgrade of the first timestamp as well.
        Check if given timestamp is present in the history.
        Upgrade or downgrade based on given direction.
        """

        direction = Direction(direction)

        if not os.path.exists(self.migrations_path):
            raise MongoMigrateException('Cannot find the migrations path: {}'.format(self.migrations_path))

        if not direction_target_is_valid(direction, target):
            raise MongoMigrateException(f"{direction.value} {target} is not a viable combination!\nOptions: {', '.join(DirectionTargetOptions.from_direction(direction) + ['timestamp (YYYYMMDDhhmmss)'])}")

        migration_walker = self.get_migration_walker()
        latest_migrated_timestamp = self._get_latest_migrated_timestamp()        

        target_timestamp = migration_walker.get_target_timestamp(target, latest_migrated_timestamp) if is_keyword_target(target) else target

        if target_timestamp != BaseFlag.base and not migration_walker.has_migration(target_timestamp):
            raise MongoMigrateException(f'Cannot find target migration {target_timestamp} in the migrations')

        if direction == Direction.up:
            self._do_upgrade(latest_migrated_timestamp, target_timestamp)
        else:
            self._do_downgrade(latest_migrated_timestamp, target_timestamp)

        print("Migrations completed!")

    def create_migration(self, title: str, message: str):
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

    def _do_upgrade(self, latest_migration: str | BaseFlag, target_migration: str):
        """
        Upgrade from latest to target migration.

        If this is the first time running an upgrade, initialize migration history.
        Identify the migrations to apply following the latest migrated version (if any)
            and including the given target migration.
        Perform upgrade method of the migration in corresponding module for each migration.
        Create migration milestone for each upgrade.

        :param target_migration:
        :return:
        """

        if not self._get_migration_history_collection():
            self.db.create_collection('migration_history')

        migration_walker = self.get_migration_walker()

        if latest_migration == migration_walker.last_migration.timestamp:
            print(f"Migrations at head; nothing to upgrade")
            return

        print(f"Upgrade: {latest_migration} -> {target_migration}")

        migrations_to_apply = migration_walker.get_migrations_between(latest_migration, target_migration)

        if len(migrations_to_apply) == 0:
            print("No new changes to apply")
            return

        # Perform migration by executing the upgrade method from the identified migrations
        sys.path.append(self.migrations_path)
        for migration in migrations_to_apply:
            migration_module = import_module(migration.basename)
            migration_instance = migration_module.Migration(self.config)
            migration_instance.upgrade()

            self._create_migration_milestone(migration.timestamp)

            print(f"{migration.previous.basename if migration.previous is not None else '.'} -> {migration.basename}")


    def _do_downgrade(self, latest_migration: str | BaseFlag, target_migration: str | BaseFlag):
        """
        Downgrade from latest migration to target migration.

        Identify the migrations to apply starting from and preceding the latest migrated version (if any),
            and up to (excluding) the given target migration.

        When rolling back, we cannot initiate the rollback from an intermediate state,
        So, we will always start from the last migrated location in the database.
        :param target_migration:
        :return:
        """
        if not self._get_migration_history_collection():
            raise MongoMigrateException("No past migrations found. Cannot perform rollback")

        if latest_migration == BaseFlag.base:
            print(f"Migrations at base; nothing to downgrade")
            return            

        print(f"Downgrade: {latest_migration} -> {target_migration}")

        migration_walker = self.get_migration_walker()
        migrations_to_apply = migration_walker.get_migrations_between(target_migration, latest_migration)
        migrations_to_apply.reverse()

        if len(migrations_to_apply) == 0:
            print("No new changes to apply")
            return

        # Perform migration by executing the downgrade method from the identified migrations
        sys.path.append(self.migrations_path)
        for migration in migrations_to_apply:
            migration_module = import_module(migration.basename)
            migration_instance = migration_module.Migration(self.config)
            migration_instance.downgrade()

            self._delete_migration_milestone(migration.timestamp)

            print(f"{migration.basename} -> {migration.previous.basename if migration.previous is not None else '.'}")


    def _get_migration_history_collection(self) -> list[str]:
        return self.db.list_collection_names(filter={'name': 'migration_history'})

    def _get_migration_history(self, db_filter=None) -> list:
        """
        Get list of past migrations from newest to oldest.
        """
        if db_filter is None:
            db_filter = {}
        return list(self.db.migration_history.find(db_filter).sort([('migration_datetime', pymongo.DESCENDING)]))

    def _create_migration_milestone(self, migration_datetime):
        self.db.migration_history.insert_one({'migration_datetime': migration_datetime,
                                              'created_on': datetime.now()})

    def _delete_migration_milestone(self, migration_datetime):
        self.db.migration_history.delete_one({'migration_datetime': migration_datetime})

    def _get_latest_migrated_timestamp(self) -> str | BaseFlag:
        """
        Get timestamp of the latest completed migration based on migration history.

        If there aren't any completed migrations (no migration history present),
            return base.
        """
        if not self._get_migration_history_collection():
            return BaseFlag.base
          
        past_migrations = self._get_migration_history()

        if len(past_migrations) == 0:
            return BaseFlag.base
        
        ret = past_migrations[0]['migration_datetime']

        return ret