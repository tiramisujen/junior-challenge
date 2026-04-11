from app.strategies.route_strategy import RouteStrategy, build_route
from app.utils.haversine import calculate_distance


class NearestNeighbourStrategy(RouteStrategy):
    """
    NearestNeighbourStrategy — YOUR TASK #3

    Implement a smarter route optimisation using the nearest-neighbour heuristic.
    The idea: when you have multiple matches on the same day (or close dates),
    choose the one that's geographically closest to where you currently are.

    This should produce shorter total distances than DateOnlyStrategy.
    """

    def optimise(self, matches: list) -> dict:
        # TODO: Implement nearest-neighbour optimisation (YOUR TASK #3)
        #
        # Pseudocode:
        # 1. Sort all matches by kickoff date
        # 2. Group matches that fall on the same day
        #    Hint: match['kickoff'].split('T')[0] gives the date string
        # 3. Start with the first match chronologically — this is your starting city
        # 4. For each subsequent day group:
        #    a. If only one match that day → add it to the route
        #    b. If multiple matches that day → pick the one whose city is closest
        #       to your current position (use calculate_distance)
        # 5. Track your "current city" as you go — update it after each match
        # 6. Return build_route(ordered_matches, 'nearest-neighbour')
        #
        # Helper you'll need:
        #   calculate_distance(lat1, lon1, lat2, lon2) → returns distance in km
        #
        # Example:
        #   dist = calculate_distance(
        #       current_city['latitude'], current_city['longitude'],
        #       candidate['city']['latitude'], candidate['city']['longitude']
        #   )
        #
        # Tips:
        # - You can use itertools.groupby or a dict to group by date
        # - Don't forget to handle the case where there's only one match on a day
        # - The first match in chronological order should always be your starting point
        sorted_matches = sorted(matches, key=lambda m: m['kickoff'])
        
        print(f"\n=== SORTED MATCHES ===")
        for m in sorted_matches:
            print(f"{m['id']}: {m['kickoff']} - {m['city']['name']}")
        
        # Group matches by date
        grouped_by_date = {}
        for match in sorted_matches:
            date = match['kickoff'].split('T')[0]
            if date not in grouped_by_date:
                grouped_by_date[date] = []
            grouped_by_date[date].append(match)
        
        print(f"\n=== GROUPED BY DATE ===")
        for date in sorted(grouped_by_date.keys()):
            matches_on_day = grouped_by_date[date]
            print(f"Date {date}: {len(matches_on_day)} match(es)")
            for m in matches_on_day:
                print(f"  - {m['id']} in {m['city']['name']}")

        # Build optimised route by selecting nearest match for each day
        ordered_matches = []
        current_city = None

        for date_index, date in enumerate(sorted(grouped_by_date.keys())):
            matches_on_day = grouped_by_date[date]
            
            print(f"\n{date}: {len(matches_on_day)} match(es)")
            
            # If only one match that day, add it
            if len(matches_on_day) == 1:
                match = matches_on_day[0]
                ordered_matches.append(match)
                current_city = match['city']
                print(f"  Only 1 match - {match['id']} in {match['city']['name']}")
            
            # If multiple matches that day, pick the nearest
            else:
                nearest_match = None
                nearest_distance = float('inf')
                
                # If this is the first day, just pick the first match
                if date_index == 0:
                    nearest_match = matches_on_day[0]
                    print(f"  {nearest_match['id']} in {nearest_match['city']['name']} (FIRST DAY - starting point)")
                    ordered_matches.append(nearest_match)
                    current_city = nearest_match['city']
                else:
                    # For subsequent days, find the nearest
                    for match in matches_on_day:
                        distance = calculate_distance(
                            current_city['latitude'], current_city['longitude'],
                            match['city']['latitude'], match['city']['longitude']
                        )
                        print(f"  {match['id']} in {match['city']['name']}: {distance:.2f}km")
                        
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_match = match
                    
                    ordered_matches.append(nearest_match)
                    current_city = nearest_match['city']
                
                print(f"  SELECTED: {nearest_match['id']}")

        # Return the optimised route
        return build_route(ordered_matches, 'nearest-neighbour')