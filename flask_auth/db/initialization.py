import click
import flask
import flask.cli

from .connection import close_db, get_connection


def init_db():
    connection = get_connection()
    with flask.current_app.open_resource('db/schema.sql') as f:
        connection.executescript(f.read().decode('utf8'))


@click.command('init-db')
@flask.cli.with_appcontext
def init_db_command():
    init_db()
    click.echo('Initiatlized the database')


# This looks like a mistake in the original because it is not called anywhere
def init_app(app):
    app.teardown_appcontext(close_db)
    app.click.add_command(init_db_command)
