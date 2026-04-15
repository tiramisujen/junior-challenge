from datetime import datetime
from typing import Optional
from app.strategies.route_strategy import BudgetResult, CostBreakdown


class CostCalculator:
    """
    CostCalculator — YOUR TASK #5

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    The calculate method should:
    1. Calculate ticket costs (sum of ticketPrice for all matches)
    2. Calculate flight costs (between consecutive cities + from origin)
    3. Calculate accommodation costs (nights × city's accommodationPerNight rate)
    4. Check feasibility (total ≤ budget AND visits USA, Mexico, Canada)
    5. Return suggestions if not feasible

    ============================================================
    HELPER METHODS PROVIDED:
    ============================================================

    The helper methods below are already implemented for you:
    - get_flight_price(): Look up flight price between two cities
    - calculate_nights_between(): Calculate nights between two dates
    - get_countries_visited(): Get list of unique countries from matches
    - get_missing_countries(): Check which required countries are missing
    - generate_suggestions(): Create cost-saving suggestions

    """

    REQUIRED_COUNTRIES = ['USA', 'Mexico', 'Canada']

    def calculate(
        self,
        matches: list,
        budget: float,
        origin_city_id: str,
        flight_prices: list
    ) -> BudgetResult:
        """
        Calculate the total cost of a trip and check if it's within budget.

        Args:
            matches: List of match dicts the user wants to attend (sorted by date)
            budget: The user's maximum budget in USD
            origin_city_id: The city where the user starts their trip
            flight_prices: All available flight prices between cities

        Returns:
            BudgetResult dict containing feasibility, costs, and suggestions
        """



        # TODO: Implement cost calculation (YOUR TASK #5)
        #
        # Pseudocode:
        # 1. Calculate ticket costs:
        print(f"\n=== STEP 1: CALCULATE TICKET COSTS ===")
        ticket_costs = sum(match['ticketPrice'] for match in matches)

        print(f"Ticket costs: ${ticket_costs:.2f}")
    
        # 2. Calculate flight costs:
        print(f"=== STEP 2: CALCULATE FLIGHT COSTS ===")
        flight_costs = 0

        # flight from origin to the first match's city
        if matches:
            first_match_city = matches[0]['city']['id']
            origin_to_first = self.get_flight_price(origin_city_id, first_match_city, flight_prices)
            flight_costs += origin_to_first
            print(f"  Origin ({origin_city_id}) → {first_match_city}: ${origin_to_first:.2f}")
        
        # flights between consecutive matches

        #    - From origin_city_id to first match's city
        #    - Between each consecutive match city (if different)
        #    - Use get_flight_price() helper to look up prices
        
        for i in range(len(matches) - 1):
            current_city = matches[i]['city']['id']
            next_city = matches[i + 1]['city']['id']
            
            flight_price = self.get_flight_price(current_city, next_city, flight_prices)
            flight_costs += flight_price
            print(f"  {current_city} → {next_city}: ${flight_price:.2f}")

        print(f"Total flight costs: ${flight_costs:.2f}\n")


        # 3. Calculate accommodation costs:
        #    - For each city visited, calculate nights stayed
        #    - Use calculate_nights_between() for dates
        #    - Multiply nights by city's accommodationPerNight
        print(f"=== STEP 3: CALCULATE ACCOMMODATION COSTS ===")
        accommodation_costs = 0
        for i, match in enumerate(matches):
            city = match['city']
            accommodation_per_night = city['accommodationPerNight']
            # calculate nights at this city
            if i < len(matches)-1:
                # not the last match - nights until next match
                current_kickoff = match['kickoff']
                next_kickoff = matches[i + 1]['kickoff']
                nights = self.calculate_nights_between(current_kickoff, next_kickoff)
            else:
                # last match, assume 1 night stay
                nights = 1
            city_accommodation = accommodation_per_night * nights
            accommodation_costs += city_accommodation
            print(f"  {city['name']}: {nights} night(s) × ${accommodation_per_night:.2f} = ${city_accommodation:.2f}")

        print(f"Total accommodation costs: ${accommodation_costs:.2f}\n")

        # 4. Build CostBreakdown with all costs and total

        print(f"=== STEP 4: BUILD COST BREAKDOWN ===")
        total_cost = ticket_costs + flight_costs + accommodation_costs
        remaining_budget = budget - total_cost
        
        print(f"  Tickets: ${ticket_costs:.2f}")
        print(f"  Flights: ${flight_costs:.2f}")
        print(f"  Accommodations: ${accommodation_costs:.2f}")
        print(f"  TOTAL: ${total_cost:.2f}")
        print(f"  Budget: ${budget:.2f}")
        print(f"  Remaining: ${remaining_budget:.2f}\n")
        
        #
        # 5. Check country constraint:
        #    - Use get_countries_visited() and get_missing_countries()
        #    - If missing countries, set feasible = False
        # Step 5: Check feasibility
        print(f"=== STEP 5: CHECK FEASIBILITY ===")
        # Get countries visited
        countries_visited = self.get_countries_visited(matches)
        print(f"  Countries visited: {countries_visited}")

        # Get missing countries
        missing_countries = self.get_missing_countries(countries_visited)
        print(f"  Missing countries: {missing_countries}")

        # 6. Check budget constraint:
        #    - If total > budget, set feasible = False
        #    - Set minimumBudgetRequired = total
        # Check if within budget
        feasible = total_cost <= budget
        print(f"  Within budget: {feasible} (${total_cost:.2f} <= ${budget:.2f})")
        
        feasible = (total_cost <= budget) and (len(missing_countries) == 0)
        # Step 7: Generate suggestions if not feasible
        suggestions = []
        is_over_budget = total_cost > budget

        if is_over_budget:
            print(f"=== STEP 6: GENERATE SUGGESTIONS ===")
            suggestions = self.generate_suggestions(matches, total_cost, budget)
            for suggestion in suggestions:
                print(f"  - {suggestion}")
            print()

        # Determine message based on feasibility
        if feasible:
            message = "Trip is feasible - within budget and all countries covered"
        else:
            if missing_countries:
                message = f"Trip not feasible - missing required countries: {', '.join(missing_countries)}"
            else:
                message = f"Trip exceeds budget by ${total_cost - budget:.2f}"
        
        # Build response dict
        result = {
            "message": message,
            "feasible": feasible,
            "costBreakdown": {
                "ticketCost": round(ticket_costs, 2),
                "flightCost": round(flight_costs, 2),
                "accommodationCost": round(accommodation_costs, 2),
                "totalCost": round(total_cost, 2)
            },
            "budget": round(budget, 2),
            "remaining": round(remaining_budget, 2),
            "countriesVisited": countries_visited,
            "missingCountries": missing_countries,
            "matchCount": len(matches),
            "suggestions": suggestions
        }

        return result
    


    
    # ============================================================
    # HELPER METHODS (Already implemented for you)
    # ============================================================

    def get_flight_price(
        self,
        from_city_id: str,
        to_city_id: str,
        flight_prices: list
    ) -> float:
        """
        Look up the flight price between two cities.
        Returns an estimated price if no direct flight exists.
        """
        if from_city_id == to_city_id:
            return 0

        for fp in flight_prices:
            if fp['originCityId'] == from_city_id and fp['destinationCityId'] == to_city_id:
                return fp['priceUsd']

        # If no direct flight, estimate based on average
        if flight_prices:
            avg_price = sum(fp['priceUsd'] for fp in flight_prices) / len(flight_prices)
            return avg_price * 1.2  # 20% markup for indirect routes
        return 300 * 1.2

    def calculate_nights_between(self, date1: str, date2: str) -> int:
        """Calculate the number of nights between two dates."""
        d1 = datetime.fromisoformat(date1.split('T')[0])
        d2 = datetime.fromisoformat(date2.split('T')[0])
        return max(0, (d2 - d1).days)

    def get_countries_visited(self, matches: list) -> list:
        """Get list of unique countries visited from matches."""
        countries = set()
        for match in matches:
            countries.add(match['city']['country'])
        return list(countries)

    def get_missing_countries(self, countries_visited: list) -> list:
        """Check which required countries (USA, Mexico, Canada) are missing."""
        return [c for c in self.REQUIRED_COUNTRIES if c not in countries_visited]

    def generate_suggestions(
        self,
        matches: list,
        total: float,
        budget: float
    ) -> list:
        """Generate cost-saving suggestions when budget is exceeded."""
        suggestions = []
        overage = total - budget

        if len(matches) > 5:
            most_expensive = max(matches, key=lambda m: m['ticketPrice'])
            suggestions.append(
                f"Consider removing the {most_expensive['homeTeam']['name']} vs "
                f"{most_expensive['awayTeam']['name']} match to save ${most_expensive['ticketPrice']}"
            )

        suggestions.append(
            f"You are ${overage:.0f} over budget. Consider reducing the number of matches."
        )

        return suggestions
