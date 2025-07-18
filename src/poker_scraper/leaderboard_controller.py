from flask import Blueprint, Response
from . import api_service 

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/placement')
def placement():
    placement_leaderboard_dataframe = api_service.get_placement_leaderboard_from_rounds()
    return placement_leaderboard_dataframe.to_json(orient="records")
@leaderboard_bp.route('/placement/html')
def placement_html():
    placement_leaderboard_dataframe = api_service.get_placement_leaderboard_from_rounds()
    return Response(f"<pre>{placement_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/percentile')
def percentile():
    percentile_leaderboard_dataframe = api_service.get_percentile_leaderboard_from_rounds()
    return percentile_leaderboard_dataframe.to_json(orient="records")
@leaderboard_bp.route('/percentile/html')
def percentile_html():
    percentile_leaderboard_dataframe = api_service.get_percentile_leaderboard_from_rounds()
    return Response(f"<pre>{percentile_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/roi')
def roi():
    roi_leaderboard_dataframe = api_service.get_roi_leaderboard_from_rounds()
    return roi_leaderboard_dataframe.to_json(orient="records")
@leaderboard_bp.route('/roi/html')
def roi_html():
    roi_leaderboard_dataframe = api_service.get_roi_leaderboard_from_rounds()
    return Response(f"<pre>{roi_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/trueskill')
def trueskill():
    trueskill_leaderboard_dataframe = api_service.get_trueskill_leaderboard_from_rounds()
    return trueskill_leaderboard_dataframe.to_json(orient="records")
@leaderboard_bp.route('/trueskill/html')
def trueskil_html():
    trueskill_info = """
        Why We Use TrueSkill™ for Rankings

        - 🎮 Used by Xbox Live for popular games like Halo, Call of Duty, Gears of War, Forza, Overwatch, Team Fortress 2, and CS:GO.
        - ♟️ Adapted by chess, Go, and board game leagues to track true skill.
        - 🏆 Ranks players by considering not just wins, but the skill level of the opponents you face.
        - 🔄 Adjusts your ranking after every game.

        Note: Your TrueSkill score is a **relative skill estimate**, not a point total or winning percentage. Higher means stronger player, but it’s not a direct measure of any one stat.
    """
    trueskill_leaderboard_dataframe = api_service.get_trueskill_leaderboard_from_rounds()
    html_from_dataframe = trueskill_info + "\n\n" + trueskill_leaderboard_dataframe.to_string(index=False)
    return Response(f"<pre>{html_from_dataframe}</pre>", mimetype='text/html')

@leaderboard_bp.route('/percentilenoroundlimit')
def percentile_no_round_limit():
    percentile_no_limit_dataframe = api_service.get_percentile_leaderboard_from_rounds_no_round_limit()
    return percentile_no_limit_dataframe.to_json(orient="records")
@leaderboard_bp.route('/percentilenoroundlimit/html')
def percentile_no_round_limit_html():
    percentile_no_limit_dataframe = api_service.get_percentile_leaderboard_from_rounds_no_round_limit()
    return Response(f"<pre>{percentile_no_limit_dataframe.to_string(index=False)}</pre>", mimetype='text/html')