#!/usr/bin/env python
from flask.ext.script import Manager, Server

from reports_manager.dashboard import app, db
from novell_libraries.config import FileConfig

cert, key = FileConfig.certs()
manager = Manager(app)
#manager.add_command("runserver", Server(ssl_context=('/etc/nginx/ssl/nginx_1.crt', '/etc/nginx/ssl/nginx_1.key')))
manager.add_command("runserver", Server(ssl_context=(cert.strip(), key.strip())))
@manager.command
def create_tables():
    "Create relational database tables."
    db.create_all()

@manager.command
def drop_tables():
    "Drop all project relational database tables. THIS DELETES DATA."
    db.drop_all()

if __name__ == '__main__':
    manager.run()


