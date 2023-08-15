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
from string import Template


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

    def migrate(self, direction, upto):
        """Public method to perform the migration - upgrade or downgrade"""
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

