# TODO: Add proper interface definitions for analytics services

from . import placement_analyzer, win_rate_analyzer, roi_analyzer, trueskill_analyzer, player_weighted_spring_graph, player_disconnectedness

# Import functions directly into the module namespace
build_players_outlasted_leaderboard = placement_analyzer.build_players_outlasted_leaderboard
build_1st_place_win_leaderboard = win_rate_analyzer.build_1st_place_win_leaderboard
build_itm_percent_leaderboard = placement_analyzer.build_itm_percent_leaderboard

build_roi_leaderboard = roi_analyzer.build_roi_leaderboard
generate_graph_image_buffer = player_weighted_spring_graph.generate_graph_image_buffer
build_player_graph = player_weighted_spring_graph.build_player_graph
get_community_avg_disconnectedness_df = player_disconnectedness.get_community_avg_disconnectedness_df

build_trueskill_leaderboard= trueskill_analyzer.build_trueskill_leaderboard
__all__ = [
    'build_players_outlasted_leaderboard',
    'build_roi_leaderboard',
    'build_trueskill_leaderboard',
    'build_1st_place_win_leaderboard',
    'build_itm_percent_leaderboard',
    'generate_graph_image_buffer',
    'build_player_graph',
    'get_community_avg_disconnectedness_df'
]
