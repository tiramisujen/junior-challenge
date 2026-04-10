from flask import Blueprint, jsonify, request
from app.models.match import Match
import re

matches_bp = Blueprint('matches', __name__)

# ============================================================
#  Matches Routes — YOUR TASK #2
#
#  Implement the REST endpoints for matches.
# ============================================================


# ============================================================
#  GET /api/matches — Return matches with optional filters
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #2)
#
# Query parameters (both optional):
#   ?city=city-atlanta    → filter by city ID
#   ?date=2026-06-14      → filter by date (YYYY-MM-DD)
#
# Hint: Use request.args.get() to extract optional query parameters.
# Use Match.query with filter_by() or filter() to apply filters.
# Order results by kickoff and convert to dicts using match.to_dict()
#
# ============================================================

@matches_bp.route('', methods=['GET'])
def get_matches():
    """
    GET endpoint to retrieve matches with optional filters.
    
    Query Parameters:
        city_id (optional): Filter matches by city ID
        date (optional): Filter matches by date in YYYY-MM-DD format
    
    Returns:
        JSON array of match objects ordered by kickoff time
    """
    # optional query parameters
    city = request.args.get('city', type=str)
    date = request.args.get('date', type=str)

    # base query
    query = Match.query

    # apply city_id filter if there is one
    if city is not None:
        query = query.filter_by(city_id=city)
    
    if date is not None:
        # Validate date format (YYYY-MM-DD) using regex
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            # error handling if format is invalid
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Filter for dates that start with the provided date
        query = query.filter(Match.kickoff.startswith(date))
    
    # order by kickoff
    matches = query.order_by(Match.kickoff).all()
    # return converted dicts
    return jsonify([match.to_dict() for match in matches]), 200


# ============================================================
#  GET /api/matches/<id> — Return a single match by ID
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #2)
#
# Hint: Use Match.query.get(id) — returns None if not found.
# Return 404 with an error message if not found.
#
# ============================================================

@matches_bp.route('/<id>', methods=['GET'])
def get_match_by_id(id):
    """
    GET endpoint to retrieve a single match by ID.
    
    Args:
        id (str): The match ID
    
    Returns:
        JSON object of the match if found
        404 error if match not found
    """
    # query for the match by it's id
    match = Match.query.get(id)

    # return 404 error if the match wasn't found
    if match is None:
        return jsonify({"error":f"Match with id: '{id}' not found" }), 404

    # else return the match as JSON
    return jsonify(match.to_dict()), 200
