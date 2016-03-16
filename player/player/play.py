# -*- coding: utf-8 -*-

import sys
import random
import json
from gevent import Greenlet
from gevent.queue import Queue

import requests

from .logger import log

class Play(Greenlet):

    def __init__(self, championship_uuid, championship_name, stage, game_uuid, game_name,
                 mode, opponent, round_no, defense_strength):
        super(Play, self).__init__()
        self.championship_uuid = championship_uuid
        self.championship_name = championship_name
        self.stage = stage
        self.game_uuid = game_uuid
        self.game_name = game_name
        self.mode = mode
        self.opponent = opponent
        self.round_no = round_no
        self.defense_strength = defense_strength

    def inform_referee(self):
        log.info("Championship:{}, Stage:{}, Game:{}, Opponent:{}, Round:{}, Mode:{}, Play: {}"
            .format(self.championship_name, self.stage, self.game_name, self.opponent,
                    self.round_no, self.mode, self.play_data))
        #TODO
        requests.post("http://localhost:5000/championships/{}/games/{}/{}"
                      .format(self.championship_uuid, self.game_uuid, self.mode),
                      data={"play_data": json.dumps(self.play_data)})

    def play(self):
        if self.mode == "attack":
            self.play_data = random.randint(1,500)
        elif self.mode == "defend":
            self.play_data = [random.randint(1,500) for i in xrange(self.defense_strength)]
        self.inform_referee()

    def _run(self):
        self.play()


class Shutdown(Greenlet):
    def __init__(self):
        super(Shutdown, self).__init__()

    def _run(self):
        log.info("Lost Game .. Shutting down")
        sys.exit(0)
