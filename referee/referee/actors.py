# -*- coding: utf-8 -*-

import gevent
from gevent import Greenlet
from gevent.queue import Queue

from sqlalchemy import inspect
import requests

from referee.model import Player, Game, Round, Championship
from referee.model import game_actor_map

from .logger import log
from .util import notify, transform_list
from .db import get_db_session, get_db_engine


class GameActor(Greenlet):

    def __init__(self, game, championship, stage):
        super(GameActor, self).__init__()

        self.inbox_a = Queue()
        self.inbox_d = Queue()
        self.game_uid = game.uid
        self.game_name = game.name
        self.game_uuid = game.uuid
        self.attacker_uid = game.p1_uid
        self.defender_uid = game.p2_uid
        self.championship_uid = championship.uid
        self.championship_uuid = championship.uuid
        self.championship_name = championship.name
        self.round_no = 1
        self.stage = stage
        self.game_over = False

    def notify_player(self, player_uid, opponent_uid, mode):
        player = Player.fetch(uid=player_uid)
        opponent = Player.fetch(uid=opponent_uid)

        data = {
            "championship_uuid": self.championship_uuid,
            "championship_name": self.championship_name,
            "game_uuid": self.game_uuid,
            "game_name": self.game_name,
            "mode": mode,
            "opponent": opponent.name,
            "stage": self.stage,
            "round_no": self.round_no,
            "defense_strength": player.defense_strength,
        }
        url = player.endpoint + "/game_info"
        notify(url, data=data)

    def notify_attacker(self):
        self.notify_player(self.attacker_uid, self.defender_uid, mode="attack")

    def notify_defender(self):
        self.notify_player(self.defender_uid, self.attacker_uid, mode="defend")

    def check_winner(self):
        self.winner_uid = self.defender_uid if self.attacker_data in self.defender_data \
                          else self.attacker_uid

    def write_round_results(self):
        r = Round(self.round_no, self.attacker_uid, self.defender_uid,
                  self.game_uid, self.championship_uid, self.attacker_data,
                  self.defender_data, self.winner_uid)
        r.save()

    def prepare_next_round(self):
        #clear remaining queue items
        self.inbox_a.queue.clear()
        self.inbox_d.queue.clear()
        self.round_no += 1

        if self.winner_uid == self.defender_uid:
            if Round.number_of_wins(self.game_uid, self.defender_uid) >= 5:
                self.game_over = True
                self.loser_uid = self.attacker_uid
            #switch_roles
            self.attacker_uid, self.defender_uid = self.defender_uid, self.attacker_uid
        else:
            if Round.number_of_wins(self.game_uid, self.attacker_uid) >= 5:
                self.game_over = True
                self.loser_uid = self.defender_uid

        if self.game_over:
            game = Game.fetch(uid=self.game_uid)
            game.winner_uid = self.winner_uid
            game.save()
            game = Game.fetch(uid=self.game_uid)
            log.debug("Winner: {}".format(game.winner_uid))

    def play_round(self):
        self.notify_attacker()
        self.notify_defender()
        self.attacker_data = self.inbox_a.get()
        self.defender_data = self.inbox_d.get()
        self.check_winner()
        self.write_round_results()
        self.prepare_next_round()

    def shutdown_loser(self):
        loser = Player.fetch(uid=self.loser_uid)
        url = loser.endpoint + "/shutdown"
        try:
            notify(url)
        except Exception:
            pass

    def close_game(self):
        self.shutdown_loser()

    def _run(self):
        self.running = True
        while self.running:
            if self.game_over:
                self.close_game()
                log.debug("Destroying game actor")
                return self.winner_uid
            self.play_round()


def start_game(game_uid, championship, stage):
    game = Game.fetch(uid=game_uid)
    log.debug("Starting Game: {}".format(game.name))
    ga = GameActor(game, championship, stage)
    ga.start()
    game_actor_map[game.uuid] = ga
    ga.join()


class ChampionshipGreenlet(Greenlet):

    def __init__(self, championship):
        super(ChampionshipGreenlet, self).__init__()
        self.championship_uid = championship.uid
        self.championship_uuid = championship.uuid
        self.championship_name = championship.name

    def get_next_stage_players(self, games, stage):
        player_uids = []

        for game in games:
            log.debug("Stage Games: {}".format(game.to_dict()))
            player_uids.append(game.winner_uid)
        try:
            next_stage_players = transform_list(player_uids)
        except Exception:
            next_stage_players = []

        log.debug("Stage players: {}".format(next_stage_players))
        return next_stage_players

    def start_games(self, game_uids, stage):

        class Championship(object):

            def __init__(self, uid, uuid, name):
                self.uid = uid
                self.uuid = uuid
                self.name = name

        championship = Championship(self.championship_uid, self.championship_uuid,
                                    self.championship_name)

        return [gevent.spawn(start_game, game_uid, championship, stage)
                for game_uid in game_uids]

    def wait(self, game_actors, stage):
        log.debug("Wating for {} stage to complete.".format(stage))
        result = gevent.joinall(game_actors)
        return [actor.value for actor in game_actors]

    def draw_games(self, stage_players, stage):
        game_uids = []
        for (p1_uid, p2_uid) in stage_players:
            name = "{}:{}-vs-{}".format(stage, p1_uid, p2_uid)
            game = Game(name, p1_uid, p2_uid, self.championship_uid, stage)
            game.save()
            game_uids.append(game.uid)
        return game_uids

    def get_game_results(self, stage):
        return Game.fetch_all(championship_uid=self.championship_uid, stage=stage)

    def play_stage(self, stage_players):

        if len(stage_players) == 4:
            stage = "QuarterFinals"
        elif len(stage_players) == 2:
            stage = "SemiFinals"
        elif len(stage_players) == 1:
            stage = "Finals"

        game_uids = self.draw_games(stage_players, stage)
        game_actors = self.start_games(game_uids, stage)
        res = self.wait(game_actors, stage)

        if stage == "Finals":
            log.info("All done!")
            return

        game_results = self.get_game_results(stage)
        next_stage_players = self.get_next_stage_players(game_results, stage)
        self.play_stage(next_stage_players)

    def init(self):
        championship = Championship.fetch(uid=self.championship_uid)
        player_uids = []
        for player in championship.players:
            player_uids.append(player.uid)
        return transform_list(player_uids)

    def _run(self):
        initial_players = self.init()
        self.play_stage(initial_players)
