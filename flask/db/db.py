import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'sqlite.db',
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():
    connection = get_connection()

    # This will probably need to be updated
    with current_app.open_resource('db/schema.sql') as f:
        connection.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initiatlized the database')


# This looks like a mistake in the original because it is not called anywhere
def init_app(app):
    app.teardown_appcontext(close_db)
    app.click.add_command(init_db_command)


try:
    init_db_command()
except sqlite3.OperationalError:
    pass  # Database already initialized
