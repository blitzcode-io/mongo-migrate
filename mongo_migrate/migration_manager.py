"""
    Module: migration_manager.py
    Author: Rahul George
    
    Description:
    This is the core of the mongo_migrate library.
    
    License:
    
    Created on: 14-08-2023
    
"""
import os.path
from datetime import datetime


class MigrationManager(object):

    NEW_MIGRATION_STRING = """
from mongodb_migrations.base import BaseMigration
    
class Migration(BaseMigration):
    def upgrade(self):
        pass
        
    def downgrade(self):
        pass
    """

    def __init__(self, config, migrations_path):
        self.config = config        # database config - host, port, db
        self.migrations_path = migrations_path

    def migrate(self, direction, upto):
        """Public method to perform the migration - upgrade or downgrade"""
        pass

    def create_migration(self, title, message):
        """Create the folder and the template migration file."""
        # Check if migration folder exists, if not create the folder,
        # Get the current datetime in YYYYMMDDHHmmSS format, evaluate the file name.
        # Create a template string.
        # Save it to a file with name evaluated.

        if not os.path.exists(self.migrations_path):
            os.makedirs(self.migrations_path)

        filename = "{}/{}_{}.py".format(
            self.migrations_path,
            datetime.now().strftime('%Y%m%d%H%M%S'),
            title)

        with open(filename, 'w') as fh:
            fh.write(self.NEW_MIGRATION_STRING)

        print('Migration file created: {}'.format(filename))

