# -*- coding: utf-8 -*-


def setup_routes(config):

    config.add_route('player_sc',
                     '/players')
    config.add_view('.views.list_all_players', route_name='player_sc',
                    request_method='GET', renderer='json')
    config.add_view('.views.create_player', route_name='player_sc',
                    request_method='POST', renderer='json')

    config.add_route('championship_players',
                     '/championships/{championship_uuid}/players')
    config.add_view('.views.list_championship_players', route_name='championship_players',
                    renderer='json', request_method='GET')
    config.add_view('.views.add_player_to_championship', route_name='championship_players',
                    renderer='json', request_method='POST')

    config.add_route('championship_games',
                     '/championships/{championship_uuid}/games')
    config.add_view('.views.list_championship_games', route_name='championship_games',
                    renderer='json', request_method='GET')

    config.add_route('championship_game_attack',
                     '/championships/{championship_uuid}/games/{game_uuid}/attack')
    config.add_view('.views.championship_game_attack', route_name='championship_game_attack',
                    renderer='json', request_method='POST')

    config.add_route('championship_game_defend',
                     '/championships/{championship_uuid}/games/{game_uuid}/defend')
    config.add_view('.views.championship_game_defend', route_name='championship_game_defend',
                    renderer='json', request_method='POST')
