# -*- coding: utf-8 -*-


def setup_routes(config):

    config.add_route('game_info',
                     '/game_info')
    config.add_view('.views.game_info', route_name='game_info',
                    request_method='POST', renderer='json')

    config.add_route('shutdown',
                     '/shutdown')
    config.add_view('.views.shutdown', route_name='shutdown',
                    request_method='POST', renderer='json')
