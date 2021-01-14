import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# returns a database connection


def get_db():
    if 'db' not in g:
        # g is an object that is unique for each request
        # it's used to store data data that might be accessed by multiple
        # functions during the request.
        # the connection is stored and reused if get_db is called a second time
        # in the same request.

        # current_app points to the Flask app handling the request
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # flask calls close_db when cleaning up after returning a response
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
