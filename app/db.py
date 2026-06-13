import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
        g.db.create_function("LOWER", 1, lambda s: s.lower() if s else "")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    """Clear the existing database and create new tables."""
    init_db()
    click.echo("Initialized the database.")


sqlite3.register_converter("DATETIME", lambda dt: datetime.fromisoformat(dt))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
