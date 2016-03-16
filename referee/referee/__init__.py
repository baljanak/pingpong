# -*- coding: utf-8 -*-

import os
import shutil
import sys
import pkg_resources

from pyramid.config import Configurator
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi

from .db import create_db, get_db_session
from .model import Championship
from .logger import log
from .routes import setup_routes
from .config import init_config


def finish_callback(request):
    get_db_session().close()


def new_request(event):
    event.request.add_finished_callback(finish_callback)


def setup_events(config):
    config.add_subscriber('.new_request', 'pyramid.events.NewRequest')


def seed_data():
    champ = Championship("Test Ping Pong Championship")
    champ.save()


def main():

    config = Configurator()
    setup_routes(config)
    setup_events(config)
    application = config.make_wsgi_app()

    ini_path = pkg_resources.resource_filename("referee", "referee.ini")
    config = init_config(ini_path)

    host = config.get("server", "host")
    port = config.getint("server", "port")

    db_path = config.get("store", "path")
    if not config.getboolean("store", "persist_on_restart"):

        if os.path.exists(db_path) and os.path.isfile(db_path):
            db_bak = db_path + ".bak"
            log.info("Backing up previous DB file to {}".format(db_bak))
            shutil.move(db_path, db_bak)

        dburi = "sqlite:///{}".format(db_path)
        create_db(dburi)
        seed_data()

    server = pywsgi.WSGIServer((host, port), application)

    log.info("Starting Referee App at {}:{}".format(host, port))
    server.serve_forever()


if __name__ == '__main__':
    main()
