import sqlite3

import flask


def get_connection():
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            'sqlite.db',
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        flask.g.db.row_factory = sqlite3.Row

    return flask.g.db


def close_db(e=None):
    db = flask.g.pop('db', None)

    if db is not None:
        db.close()
