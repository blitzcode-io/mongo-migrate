# mongo-migrate

Create mongodb migrations using python. 

MongoDB is a schemaless database but most of the time the data that you store in the database will end up have a loose schema. 
The python library is aimed to solve the below problem scenarios: 
  1. As your project grows, the schema also changes and grows with it. When you want to go back to a specific version of the code and run that version. Most of the time, you do not remember the database schema used with the partical version of code. This is where creating a migration file and keeping it under the version control along with your code helps. You can retrace the steps to that particular version of schema. 
  2. Lastly, even if your code base is in another language, you can use the mongo-migrate package to create migrations. Exactly for this reason, mongo-migrate is coming out of the box with lot of sub commands. 

The mongo-migrate library can create migrations, perform upgrade and downgrade operations.

# Usage

    usage: mongo-migrate [-h] {create,upgrade,downgrade} ...
    
    positional arguments:
      {create,upgrade,downgrade}
        create              create a new migration
        upgrade             upgrade the database to the specific migration
        downgrade           downgrade the database to the specific migration
    
    optional arguments:
      -h, --help            show this help message and exit


### Create Migrations

    usage: mongo-migrate create [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--title TITLE] --message MESSAGE
    
    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           provide the database host
      --port PORT           provide the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --title TITLE         provide the folder to store migrations
      --message MESSAGE     provide the folder to store migrations

Example command would look like:
    
    mongo-migrate create --host 127.0.0.1 --port 27017 --database test --message 'first migration'


### Upgrade database

    usage: mongo-migrate upgrade [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--upto UPTO]

    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           provide the database host
      --port PORT           provide the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --upto UPTO           provide the folder to store migrations

Example command would look like:
    
    mongo-migrate upgrade --host 127.0.0.1 --port 27017 --database test --upto 20230815092813

### Downgrade database

    usage: mongo-migrate downgrade [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--upto UPTO]

    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           provide the database host
      --port PORT           provide the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --upto UPTO           provide the folder to store migrations

Example command would look like:
    
    mongo-migrate downgrade --host 127.0.0.1 --port 27017 --database test --upto 20230815092813


# Installation

    pip install mongo-migrate

# Planned Features
  * Support for connection string, 
  * Support for authenticated databases
  * Support for configuration file to eliminate retyping the CLI arguments. 
  * More shortcuts for migration generation
  * 
