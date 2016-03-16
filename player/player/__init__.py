# -*- coding: utf-8 -*-

import socket
import json
import sys
import pkg_resources
from ConfigParser import SafeConfigParser

from pyramid.config import Configurator
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
import requests

from .logger import log
from .routes import setup_routes


def get_free_port():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('127.0.0.1', 0))
  addr, port = s.getsockname()
  s.close()
  return port


def register_player(referee_host, referee_port, player_data):
    res = requests.post('http://{}:{}/players'.format(referee_host, referee_port),
                        data=player_data)

    if res.status_code != 200:
        log.error("Referee responded with {}. Exiting ..".format(res.status_code))
        sys.exit(-1)
    return json.loads(res.json())


def add_player_championship(referee_host, referee_port, player_name, champ_uuid):
    res = requests.post('http://{}:{}/championships/{}/players'
                        .format(referee_host, referee_port, champ_uuid),
                        data={'player_name': player_name})

    if res.status_code != 200:
        log.error("Referee responded with {}. Exiting ..".format(res.status_code))
        sys.exit(-1)
    return json.loads(res.json())


def main():

    config = Configurator()
    setup_routes(config)
    application = config.make_wsgi_app()

    config = SafeConfigParser()
    ini_path = pkg_resources.resource_filename("player", "player.ini")
    config.read(ini_path)
    host = config.get("server", "host")
    port = get_free_port()

    referee_host = config.get("referee", "host")
    referee_port = config.get("referee", "port")
    player_data = dict(config.items("info"))
    player_data['endpoint'] = 'http://{}:{}'.format(host, port)

    #TODO
    try:
      player_data['name'] = sys.argv[1]
      player_data['defense_strength'] = sys.argv[2]
    except:
      pass

    r = register_player(referee_host, referee_port, player_data)
    add_player_championship(referee_host, referee_port,
                            player_data['name'], r['championship_uuid'])

    server = pywsgi.WSGIServer((host, port), application)
    log.info("Starting Server at {}:{}".format(host, port))
    server.serve_forever()


if __name__ == '__main__':
    main()
