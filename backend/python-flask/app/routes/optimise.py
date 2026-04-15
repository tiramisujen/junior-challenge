from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.flight_price import FlightPrice
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy
# Tip: You can also import DateOnlyStrategy to compare results
from app.strategies.date_only_strategy import DateOnlyStrategy
from app.utils.cost_calculator import CostCalculator
from app.bonus.best_value_finder import BestValueFinder

optimise_bp = Blueprint('optimise', __name__)

# ============================================================
#  Route Optimisation — YOUR TASK #3 and #5
#
#  Implement route optimisation and budget calculation endpoints.
# ============================================================


# ============================================================
#  POST /api/route/optimise — Optimise a travel route
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #3)
#
# Request body: { "matchIds": ["match-1", "match-5", "match-12", ...] }
#
# Steps:
#   1. Extract matchIds from the request JSON
#   2. Fetch full match data from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Create a strategy instance: NearestNeighbourStrategy()
#      (or DateOnlyStrategy() to test with the working example first)
#   5. Call strategy.optimise(match_dicts)
#   6. Return the optimised route as JSON
#
# TIP: Start by using DateOnlyStrategy to verify your endpoint works,
# then switch to NearestNeighbourStrategy once you've implemented it.
#
# ============================================================

@optimise_bp.route('/optimise', methods=['POST'])
def optimise():
    """
    POST endpoint to optimise a travel route given a list of matches.
    
    Request body:
        { "matchIds": ["match-1", "match-5", "match-12", ...] }
    
    Returns:
        JSON object with optimised route
    """
    # Step 1: Extract matchIds from request JSON
    data = request.get_json()
    match_ids = data.get('matchIds', [])

    # Validate that matchIds is provided
    if not match_ids:
        return jsonify({"error": "matchIds array is required"}), 400

    # Step 2: Fetch full match data from database
    matches = _fetch_matches_by_ids(match_ids)
    if not matches:
        return jsonify({"error": "No matches found"}), 404
    
    print(f"Fetched {len(matches)} matches from database")
    
    # Step 3: Convert matches to dicts
    match_dicts = [match.to_dict() for match in matches]

    # Step 4: Create strategy instance and optimise
    #strategy = DateOnlyStrategy()
    strategy = NearestNeighbourStrategy()
    optimised_matches = strategy.optimise(match_dicts)
    countries_visited = CostCalculator().get_countries_visited(match_dicts)
    missing_countries = CostCalculator().get_missing_countries(countries_visited)
    optimised_matches['countriesVisited'] = countries_visited
    optimised_matches['missingCountries'] = missing_countries
    
    return jsonify(optimised_matches), 200

# ============================================================
#  POST /api/route/budget — Calculate trip costs and check budget
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #5)
#
# Request body:
# {
#   "budget": 5000.00,
#   "matchIds": ["match-1", "match-5", "match-12", ...],
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget, matchIds, and originCityId from request JSON
#   2. Fetch matches by IDs from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a CostCalculator instance
#   6. Call calculator.calculate(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BudgetResult as JSON
#
# IMPORTANT CONSTRAINTS:
#   - User MUST attend at least 1 match in each country (USA, Mexico, Canada)
#   - If the budget is insufficient, return feasible=False with:
#     - minimumBudgetRequired: the actual cost
#     - suggestions: ways to reduce cost
#   - If countries are missing, return feasible=False with:
#     - missingCountries: list of countries not covered
#
# ============================================================
@optimise_bp.route('/budget', methods=['POST'])
def budget_optimise():
    """
        POST endpoint to calculate trip costs and check budget.
        
        Request body:
            {
                "budget": 5000.00,
                "matchIds": ["match-1", "match-5", "match-12", ...],
                "originCityId": "city-atlanta"
            }
        
        Returns:
            JSON object with budget calculation result
    """
    
    # step 1: Extract budget, matchIds and originCityId from the request
    data = request.get_json()
    budget = data.get('budget')
    match_ids = data.get('matchIds', [])
    origin_city_id = data.get('originCityId')

    # Debug: print what we received
    print(f"Received budget: {budget}")
    print(f"Received matchIds: {match_ids}")
    print(f"Received originCityId: {origin_city_id}")
    
    # step 2: Fetch the matches by their id from the db
    matches = _fetch_matches_by_ids(match_ids)
    if not matches:
        return jsonify({"error": "No matches found"}), 404
    
    print(f"Fetched {len(matches)} matches from database")
    
    # step 3: convert the matches to dicts
    match_dicts = [match.to_dict() for match in matches]

    print(f"Converted matches to dicts: {len(match_dicts)} matches")
    
    # step 4: fetch all of the flight prices from the db
    flight_prices_dicts = _fetch_flight_prices()

    # DEBUG: Print the structure of a flight price
    if flight_prices_dicts:
        print(f"Flight price structure: {flight_prices_dicts[0]}")

    print(f"Fetched {len(flight_prices_dicts)} flight prices from database")
    
    # step 5: create an instance of the CostCalculator and call calculate()
    calculator = CostCalculator()
    budget_result = calculator.calculate(match_dicts, budget, origin_city_id, flight_prices_dicts)

    print(f"Budget calculation result: {budget_result}")
    
    return jsonify({
        "message": "Step 5 complete - budget calculated",
        "result": budget_result
    }), 200

# ============================================================
#  POST /api/route/best-value — Find best match combination within budget
# ============================================================
#
# TODO: Implement this endpoint (BONUS CHALLENGE #1)
#
# Request body:
# {
#   "budget": 5000.00,
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget and originCityId from request JSON
#   2. Fetch all available matches from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a BestValueFinder instance
#   6. Call finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BestValueResult as JSON
#
# Requirements:
#   - Find the maximum number of matches that fit within budget
#   - Must include at least 1 match in each country (USA, Mexico, Canada)
#   - Minimum 5 matches required
#   - Return optimised route with cost breakdown
#
# ============================================================
@optimise_bp.route('/best-value', methods=['POST'])
def best_value():
    """
    POST endpoint to find the best match combination within budget.
    
    Request body:
        {
            "budget": 5000.00,
            "originCityId": "city-atlanta"
        }
    
    Returns:
        JSON object with best value route and cost breakdown
    """
    # step 1: Extract budget and originCityId from request JSON
    data = request.get_json()
    budget = data.get('budget')
    origin_city_id = data.get('originCityId')

    # debug: print what we received
    print(f"Received budget: {budget}")
    print(f"Received originCityId: {origin_city_id}")

    # step 2: fetch all available matches from the database
    matches = _fetch_all_matches()
    if not matches:
        return jsonify({"error": "No matches available in database"}), 404
    
    print(f"Fetched {len(matches)} matches from database")
    # step 3: convert matches to dicts
    match_dicts = [match.to_dict() for match in matches]
    
    print(f"Converted matches to dicts: {len(match_dicts)} matches")
    
    # step 4: fetch all flight prices from the database
    flight_prices_dicts = _fetch_flight_prices()
    
    # debug: print the structure of a flight price
    if flight_prices_dicts:
        print(f"Flight price structure: {flight_prices_dicts[0]}")
    
    print(f"Fetched {len(flight_prices_dicts)} flight prices from database")
    
    # step 5: create a BestValueFinder instance
    finder = BestValueFinder()
    
    print(f"BestValueFinder instance created")
    
    # step 6: call finder.find_best_value()
    best_value_result = finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices_dicts)
    
    print(f"Best value calculation result: {best_value_result}")
    
    # step 7: return the BestValueResult as JSON
    return jsonify({
        "message": "Best value route found",
        "result": best_value_result
    }), 200

def _extract_request_data(data, required_fields):
    """helper function to extract and validate request data"""
    extracted = {}
    for field in required_fields:
        value = data.get(field)
        if value is None:
            return None, jsonify({"error": f"Missing required field: {field}"}), 400
        extracted[field] = value
    return extracted, None, None

def _fetch_matches_by_ids(match_ids):
    """helper function to fetch matches by their IDs"""
    matches = []
    for match_id in match_ids:
        match = Match.query.get(match_id)
        if match is None:
            return None  # just return None on error
        matches.append(match)
    return matches

def _fetch_all_matches():
    """helper function to fetch all matches from database"""
    return Match.query.all()

def _fetch_flight_prices():
    """helper function to fetch all flight prices from database"""
    flight_prices = FlightPrice.query.all()
    return [fp.to_dict() for fp in flight_prices]