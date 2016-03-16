# -*- coding: utf-8 -*-

import json
from pyramid.view import view_config

from referee.model import Player
from referee.model import Championship
from referee.model import Game, game_actor_map
from referee.logger import log
from referee.actors import GameActor, ChampionshipGreenlet


@view_config(route_name='championship_players')
def list_championship_players(request):
    championship_uuid = request.matchdict.get('championship_uuid')
    log.debug("championship uuid: {}".format(championship_uuid))
    championship = Championship.fetch(uid=championship_uuid)
    return json.dumps([u.to_dict() for u in championship.players])


@view_config(route_name='championship_players')
def add_player_to_championship(request):

    championship_uuid = request.matchdict.get('championship_uuid')
    championship = Championship.fetch(uuid=championship_uuid)

    if len(championship.players) >= 8:
        return json.dumps({'status': 404})

    player_name = request.params.get('player_name')
    player = Player.fetch(name=player_name)

    log.debug("Champ ID: {}".format(championship.uid))
    try:
        championship.add_player(player)
        championship.save()
    except Exception:
        pass

    if len(championship.players) == 8:
        log.info("All players have registered. Starting Championship .. ")
        ChampionshipGreenlet(championship).start()

    return json.dumps({'status': 'ok'})


@view_config(route_name='players_sc')
def create_player(request):
    log.debug("hello there")
    player_data = request.params
    log.debug("player_data = {}".format(player_data))

    player = Player.fetch(name=player_data['name'])
    if not player:
        player = Player(data=player_data)
        player.save()
    else:
        log.debug("Player {} already registered".format(player.name))

    ch = Championship.fetch()
    rt_dict = player.to_dict()
    rt_dict['championship_uuid'] = ch.uuid

    return json.dumps(rt_dict)


@view_config(route_name='players_sc')
def list_all_players(request):
    return json.dumps([p.to_dict() for p in Player.list()])


@view_config(route_name='championship_games')
def list_championship_games(request):
        championship_uuid = request.matchdict.get('championship_uuid')
        log.debug("championship uuid: {}".format(championship_uuid))
        championship = Championship.fetch(uid=championship_uuid)
        return json.dumps([g.to_dict() for g in championship.games])


@view_config(route_name='championship_game_attack')
def championship_game_attack(request):
    game_uuid = request.matchdict.get('game_uuid')
    play_data = request.params.get('play_data')
    log.debug("Attacker data: {}".format(play_data))
    ga = game_actor_map[game_uuid]
    ga.inbox_a.put_nowait(play_data)

    return json.dumps({"status": 200})

@view_config(route_name='championship_game_defend')
def championship_game_defend(request):
    game_uuid = request.matchdict.get('game_uuid')
    play_data = request.params.get('play_data')
    log.debug("Defender data: {}".format(play_data))
    ga = game_actor_map[game_uuid]
    ga.inbox_d.put_nowait(play_data)

    return json.dumps({"status": 200})
