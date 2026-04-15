from datetime import datetime
from typing import TypedDict, Optional
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy


class BestValueResult(TypedDict):
    """Response for best value finder."""
    withinBudget: bool
    matches: list
    route: Optional[dict]
    costBreakdown: dict
    countriesVisited: list
    matchCount: int
    message: str


class BestValueFinder:
    """
    BestValueFinder — BONUS CHALLENGE #1

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    Find the best combination of matches within a given budget.

    Requirements:
    - Maximize the number of matches that fit within budget
    - Must include at least 1 match in each country (USA, Mexico, Canada)
    - Minimum 5 matches required
    - Return optimised route with cost breakdown

    This is a combinatorial optimisation problem. You can use:
    - Greedy approach: Start with cheapest matches, ensure country coverage
    - Dynamic programming: Find optimal subset within budget
    - Heuristic approach: Start with required countries, add cheapest remaining

    ============================================================
    HELPER METHODS PROVIDED:
    ============================================================

    Use the helper methods below in your implementation:
    - get_matches_by_country(): Group matches by country
    - get_flight_price(): Look up flight price between cities
    - calculate_trip_cost(): Calculate total cost for a set of matches

    """

    REQUIRED_COUNTRIES = ['USA', 'Mexico', 'Canada']

    def find_best_value(
        self,
        all_matches: list,
        budget: float,
        origin_city_id: str,
        flight_prices: list
    ) -> BestValueResult:
        """
        Find the best value combination of matches within budget.

        Args:
            all_matches: All available matches
            budget: Maximum budget in USD
            origin_city_id: Starting city for the trip
            flight_prices: Available flight prices

        Returns:
            BestValueResult with the optimal match selection
        """
        # TODO: Implement best value finder (BONUS CHALLENGE #1)
        #
        # Suggested approach (greedy):
        # 1. First, ensure country coverage:
        #    - Pick the cheapest match from each required country
        #    - This guarantees we visit USA, Mexico, and Canada
        #
        # 2. Sort remaining matches by "value" (e.g., ticket price / quality)
        #
        # 3. Greedily add matches while staying within budget:
        #    - For each candidate match, calculate if adding it keeps us in budget
        #    - Consider both ticket price AND added flight/accommodation costs
        #
        # 4. Ensure minimum 5 matches:
        #    - If we can't reach 5 matches within budget, return withinBudget = False
        #    - Set message explaining the constraint
        #
        # 5. Build the optimised route using NearestNeighbour
        #
        # 6. Return BestValueResult with:
        #    - withinBudget: True/False
        #    - matches: selected matches
        #    - route: optimised travel route
        #    - costBreakdown: detailed costs
        #    - countriesVisited: list of countries
        #    - matchCount: number of matches
        #    - message: description of result
        #raise NotImplementedError("Not implemented — this is a bonus challenge!")
        
        # step 1: all three countries are covered
        matches_by_country = self.get_matches_by_country(all_matches)
        
        selected_matches = []
        for country in self.REQUIRED_COUNTRIES:
            if country not in matches_by_country:
                # country not available
                return {
                    'withinBudget': False,
                    'matches': [],
                    'route': None,
                    'costBreakdown': {},
                    'countriesVisited': [],
                    'matchCount': 0,
                    'message': f'Country {country} has no available matches'
                }
            
            # pick the cheapest match from this country
            cheapest = min(matches_by_country[country], key=lambda m: m['ticketPrice'])
            selected_matches.append(cheapest)
        
        print(f"step 1 complete - selected cheapest match from each required country: {len(selected_matches)} matches")

        # step 2: sort remaining matches by ticketPrice
        remaining_matches = [m for m in all_matches if m not in selected_matches]
        remaining_matches.sort(key=lambda m: m['ticketPrice'])
            
        print(f"step 2 complete - sorted {len(remaining_matches)} remaining matches by ticket price")

        # step 3: greedily add matches while staying within budget
        for match in remaining_matches:
            candidate_matches = selected_matches + [match]
            trip_cost = self.calculate_trip_cost(candidate_matches, origin_city_id, flight_prices)
            
            if trip_cost <= budget:
                selected_matches.append(match)
                print(f"added match '{match['id']}' - trip cost: ${trip_cost:.2f}")
            else:
                print(f"cannot add match '{match['id']}' - would exceed budget (${trip_cost:.2f} > ${budget:.2f})")
        
        print(f"step 3 complete - selected {len(selected_matches)} matches within budget")

        # step 4: ensure minimum 5 matches
        if len(selected_matches) < 5:
            return {
                'withinBudget': False,
                'matches': selected_matches,
                'route': None,
                'costBreakdown': {},
                'countriesVisited': list(self.REQUIRED_COUNTRIES),
                'matchCount': len(selected_matches),
                'message': f'Could not find enough matches within budget. Found {len(selected_matches)} matches, need minimum 5'
            }
        
        print(f"step 4 complete - minimum 5 matches requirement met: {len(selected_matches)} matches")
        # step 5: build the optimised route using NearestNeighbour
        strategy = NearestNeighbourStrategy()
        optimised_route = strategy.optimise(selected_matches)
    
        print(f"step 5 complete - optimised route built")

        # step 6: return BestValueResult
        trip_cost = self.calculate_trip_cost(selected_matches, origin_city_id, flight_prices)
        countries_visited = list(set(m['city']['country'] for m in selected_matches))
        
        cost_breakdown = {
            'ticketCost': sum(m['ticketPrice'] for m in selected_matches),
            'flightCost': trip_cost - sum(m['ticketPrice'] for m in selected_matches),  # simplified
            'totalCost': trip_cost
        }
        return {
                'withinBudget': True,
                'matches': selected_matches,
                'route': optimised_route,
                'costBreakdown': cost_breakdown,
                'countriesVisited': countries_visited,
                'matchCount': len(selected_matches),
                'message': f'Found optimal combination of {len(selected_matches)} matches within budget'
            }





        


    # ============================================================
    # HELPER METHODS (Already implemented for you)
    # ============================================================

    def get_matches_by_country(self, matches: list) -> dict:
        """Group matches by their country."""
        by_country = {}
        for match in matches:
            country = match['city']['country']
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(match)
        return by_country

    def get_flight_price(
        self,
        from_city_id: str,
        to_city_id: str,
        flight_prices: list
    ) -> float:
        """Look up the flight price between two cities."""
        if from_city_id == to_city_id:
            return 0

        for fp in flight_prices:
            if fp['originCityId'] == from_city_id and fp['destinationCityId'] == to_city_id:
                return fp['priceUsd']

        if flight_prices:
            avg_price = sum(fp['price'] for fp in flight_prices) / len(flight_prices)
            return avg_price * 1.2
        return 300 * 1.2

    def calculate_trip_cost(
        self,
        matches: list,
        origin_city_id: str,
        flight_prices: list
    ) -> float:
        """Calculate the total cost for a set of matches."""
        if not matches:
            return 0

        sorted_matches = sorted(matches, key=lambda m: m['kickoff'])

        # Ticket costs
        ticket_cost = sum(m['ticketPrice'] for m in matches)

        # Flight costs
        flight_cost = self.get_flight_price(
            origin_city_id,
            sorted_matches[0]['city']['id'],
            flight_prices
        )
        for i in range(1, len(sorted_matches)):
            flight_cost += self.get_flight_price(
                sorted_matches[i - 1]['city']['id'],
                sorted_matches[i]['city']['id'],
                flight_prices
            )

        # Accommodation costs (simplified)
        accommodation_cost = 0.0
        for i, match in enumerate(sorted_matches):
            nights = 1  # At least one night per match
            if i < len(sorted_matches) - 1:
                d1 = datetime.fromisoformat(match['kickoff'].split('T')[0])
                d2 = datetime.fromisoformat(sorted_matches[i + 1]['kickoff'].split('T')[0])
                nights = max(1, (d2 - d1).days)
            accommodation_cost += nights * match['city']['accommodationPerNight']

        return ticket_cost + flight_cost + accommodation_cost
    
