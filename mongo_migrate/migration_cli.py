"""
    Module: migration_cli.py
    Author: Rahul George
    
    Description:
        This module abstracts away all the CLI interactions.
        Every cli command will be added as an argparse sub-parser but in the end, it will call
         the MigrationManager class.
        The decision to go with argparse is to keep the tool dependency minimal.
    
    License:
    
    Created on: 14-08-2023
    
"""
import argparse

from mongo_migrate.enums import Direction, DirectionTargetOptions
from mongo_migrate.exceptions import MongoMigrateException
from mongo_migrate.config import ConfigManager
from mongo_migrate.migration_manager import MigrationManager
from mongo_migrate.utils import slugify_message

config_manager = ConfigManager()

def add_common_arguments(parser: argparse.ArgumentParser):
    """Common parser arguments"""
    parser.add_argument('--host', help='the database host (overrides .env)', default=None, action='store', dest='host')
    parser.add_argument('--port', help='the database port (overrides .env)', default=None, action='store', dest='port')
    parser.add_argument('--database', help='the database name (overrides .env)', default=None, action='store', dest='database')
    parser.add_argument('--migrations', help='provide the folder to store migrations. By default creates migrations/', default=None, action='store', dest='migrations')    


def subparser_for_create(subparsers):
    """Subparser for create command"""
    create_subparser = subparsers.add_parser('create', help='create a new migration')
    create_subparser.set_defaults(func=create_migration)

    add_common_arguments(create_subparser)

    create_subparser.add_argument('--message', help='short message that will be saved as a comment inside the migration file', required=True, action='store', dest='message')
    create_subparser.add_argument('--title', help='short title that will be used in the file name. Default: contents of --message', default=None, action='store', dest='title')


def create_migration(args):
    """Entry point for create migration command"""
    config = config_manager.get_config(args)
    migrations = config_manager.get_migrations(args)
    m = MigrationManager(config, migrations)
    m.create_migration(args.title or slugify_message(args.message), args.message)

def add_migrate_arguments(parser: argparse.ArgumentParser, type: str):
    """
    Add target migration timestamp argument.
    """
    target_migration_help = f"target migration timestamp or keyword (options: {', '.join(DirectionTargetOptions.from_direction(type))})"
    parser.add_argument('target_migration', nargs="?", help=target_migration_help, action='store')
    parser.add_argument('--upto', help=target_migration_help, action='store', dest='upto')
    parser.add_argument('--type', help=argparse.SUPPRESS, action='store', dest='type', default=type)


def subparser_for_upgrade(subparsers):
    """Subparser for upgrade command"""
    upgrade_subparser = subparsers.add_parser(Direction.up.value, help='upgrade the database to the target migration version')
    upgrade_subparser.set_defaults(func=migrate)

    add_common_arguments(upgrade_subparser)
    add_migrate_arguments(upgrade_subparser, Direction.up.value)


def subparser_for_downgrade(subparsers):
    """Subparser for upgrade command"""
    upgrade_subparser = subparsers.add_parser(Direction.down.value, help='downgrade the database to the target migration version')
    upgrade_subparser.set_defaults(func=migrate)

    add_common_arguments(upgrade_subparser)
    add_migrate_arguments(upgrade_subparser, Direction.down.value)


def migrate(args):
    """Entry point for both upgrade and downgrade"""
    target_migration = args.target_migration or args.upto
    if target_migration is None:
        raise MongoMigrateException(f"Provide target migration via positional argument or --upto flag")

    config = config_manager.get_config(args)
    migrations = config_manager.get_migrations(args)
    m = MigrationManager(config, migrations)
    m.migrate(args.type, target_migration)


def parse_arguments():
    parser = argparse.ArgumentParser(prog='mongo-migrate')
    subparsers = parser.add_subparsers()

    # Add subparser methods below
    subparser_for_create(subparsers)
    subparser_for_upgrade(subparsers)
    subparser_for_downgrade(subparsers)

    # Generic parse call
    args = parser.parse_args()
    try:
        args.func(args)
    except MongoMigrateException as e:
        parser.error(str(e))


def main():
    parse_arguments()


if __name__ == '__main__':
    main()
