# -*- coding: utf-8 -*-

import sys
import json
from pyramid.view import view_config

from .play import Play, Shutdown
from .logger import log


@view_config(route_name='game_info')
def game_info(request):

    championship_uuid = request.params.get('championship_uuid')
    championship_name = request.params.get('championship_name')
    stage = request.params.get('stage')
    game_uuid = request.params.get('game_uuid')
    game_name = request.params.get('game_name')
    mode = request.params.get('mode')
    opponent = request.params.get('opponent')
    round_no = request.params.get('round_no')
    defense_strength = int(request.params.get('defense_strength'))

    log.info("Championship:{}, Stage:{}, Game:{}, Opponent:{}, Round:{}, Mode:{}"
             .format(championship_name, stage, game_name, opponent, round_no, mode))

    play = Play(championship_uuid, championship_name, stage, game_uuid, game_name,
                mode, opponent, round_no, defense_strength)
    play.start()
    return json.dumps({'status': 'ok'})


@view_config(route_name='shutdown')
def shutdown(request):
    Shutdown().start()
    return json.dumps({'status': 'ok'})
