# Welcome to mongo-migrate

Migrate Mongodb seamlessly using Python and mongo-migrate. 

MongoDB is a schemaless database but most of the time the data that you store in the database will end up have a loose schema. 
The Python library is aimed to solve the below problem scenarios: 
  1. As your project grows, the schema also changes and grows with it. When you want to go back to a specific version of the code and run that version. Most of the time, you do not remember the database schema used with the particular version of code. This is where creating a migration file and keeping it under version control along with your code helps. You can retrace the steps to that particular version of the schema. 
  2. Lastly, even if your code base is in another language, you can use the Mongo-migrate package to create migrations. Exactly for this reason, mongo-migrate is coming out of the box with a lot of subcommands. 

You can read my the detailed article [here](https://rahulgeorge.hashnode.dev/migrate-mongodb-data-seamlessly-with-mongo-migrate-and-python)

The mongo-migrate library can create migrations, and perform upgrade and downgrade operations.

### Installation

    pip install mongo-migrate

### Usage

    usage: mongo-migrate [-h] {create,upgrade,downgrade} ...
    
    positional arguments:
      {create, upgrade, downgrade}
        create              create a new migration
        upgrade             upgrade the database to the specific migration
        downgrade           downgrade the database to the specific migration
    
    optional arguments:
      -h, --help            show this help message and exit

## Key Features

### Create Migrations

    usage: mongo-migrate create [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--title TITLE] --message MESSAGE
    
    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           the database host
      --port PORT           the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --title TITLE         title will be used in the file name
      --message MESSAGE     message will be recorded as a comment inside the migration file

An example command would look like this:
    
    mongo-migrate create --host 127.0.0.1 --port 27017 --database test --message 'first migration'


### Upgrade database

    usage: mongo-migrate upgrade [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--upto UPTO]

    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           the database host
      --port PORT           the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --upto UPTO           target migration timestamp

An example command would look like this:
    
    mongo-migrate upgrade --host 127.0.0.1 --port 27017 --database test --upto 20230815092813

### Downgrade database

    usage: mongo-migrate downgrade [-h] [--host HOST] [--port PORT] [--database DATABASE] [--migrations MIGRATIONS] [--upto UPTO]

    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           the database host
      --port PORT           the database port
      --database DATABASE   provide the database name
      --migrations MIGRATIONS
                            provide the folder to store migrations
      --upto UPTO           target migration timestamp

An example command would look like this:
    
    mongo-migrate downgrade --host 127.0.0.1 --port 27017 --database test --upto 20230815092813

## Planned Enhancements

Our commitment to continuous improvement includes planned features such as:
  * Support for connection string, 
  * Support for authenticated databases
  * Configuration Files: Eliminate the need for repetitive CLI arguments. 
  * More migration generation shortcuts

## Get Involved
If you encounter any issues, please raise it as a ticket in the [issue tracker.](https://github.com/blitzcode-io/mongo-migrate/issues)
If you like to contribute to this open-source project, [let me know](https://www.linkedin.com/in/rahultgeorge05). 

