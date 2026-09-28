"""Gold names API controller - exposes full-season-attendance ("golded") players by bar."""
from flask import Blueprint, jsonify
from ..services import gold_names_service

gold_names_bp = Blueprint('goldnames', __name__, url_prefix='/api/goldnames')


@gold_names_bp.route('/goldnamesbybar', methods=['GET'])
def get_gold_names_by_bar():
    """
    Get players who played every round this season for each bar.

    These players have their name golded on that bar's Keep The Score page.
    This is independent of Saturday tournament qualification/availability.
    """
    gold_names_by_bar = gold_names_service.get_gold_names_by_bar()
    return jsonify(gold_names_by_bar)
