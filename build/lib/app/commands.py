import os
import click
from flask.cli import AppGroup

db_cli = AppGroup('db')

@db_cli.command('create')
def create_db():
    import app.models.db as db
    db.init_db()
