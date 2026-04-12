import pytest
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy


class TestNearestNeighbourStrategy:
    """
    NearestNeighbourStrategyTest — feature/BE_004

    Unit tests for the NearestNeighbourStrategy.

    """

    def setup_method(self):
        self.strategy = NearestNeighbourStrategy()

    def test_happy_path_returns_valid_route(self):
        """Should return a valid route for multiple matches (happy path)"""
        
        # Arrange: Create an array of matches across different cities and dates
        matches = [
                    {
                        "id": "match-1",
                        "homeTeam": {
                            "id": "team-mexico",
                            "name": "Mexico",
                            "code": "MEX",
                            "group": "A"
                            },
                        "awayTeam": {
                            "id": "team-south-africa",
                            "name": "South Africa",
                            "code": "RSA",
                            "group": "A"
                            },
                        "city": {
                            "id": "city-mexico-city",
                            "name": "Mexico City",
                            "country": "Mexico",
                            "latitude": 19.3029,
                            "longitude": -99.1505,
                            "stadium": "Estadio Azteca",
                            "accommodationPerNight": 110.0
                            },
                        "kickoff": "2026-06-11T17:00:00Z",
                        "group": "A",
                        "matchDay": 1,
                        "ticketPrice": 120.0
                    },
                    {
                        "id": "match-4",
                        "homeTeam": {
                            "id": "team-qatar",
                            "name": "Qatar",
                            "code": "QAT",
                            "group": "B"
                            },
                        "awayTeam": {
                            "id": "team-switzerland",
                            "name": "Switzerland",
                            "code": "SUI",
                            "group": "B"
                            },
                        "city": {
                            "id": "city-houston",
                            "name": "Houston",
                            "country": "USA",
                            "latitude": 29.6847,
                            "longitude": -95.4107,
                            "stadium": "NRG Stadium",
                            "accommodationPerNight": 150.0
                            },
                        "kickoff": "2026-06-12T17:00:00Z",
                        "group": "B",
                        "matchDay": 1,
                        "ticketPrice": 85.0
                    },
                    {
                        "id": "match-5",
                        "homeTeam": {
                            "id": "team-brazil",
                            "name": "Brazil",
                            "code": "BRA",
                            "group": "C"
                            },
                        "awayTeam": {
                            "id": "team-morocco",
                            "name": "Morocco",
                            "code": "MAR",
                            "group": "C"
                            },
                        "city": {
                            "id": "city-new-york",
                            "name": "New York / New Jersey",
                            "country": "USA",
                            "latitude": 40.8128,
                            "longitude": -74.0742,
                            "stadium": "MetLife Stadium",
                            "accommodationPerNight": 300.0
                        },
                        "kickoff": "2026-06-12T19:00:00Z",
                        "group": "C",
                        "matchDay": 1,
                        "ticketPrice": 175.0
                    }
                    ]
        
        # Act: Call self.strategy.optimise(matches)
        result = self.strategy.optimise(matches)

        # Assert: Verify the result has stops, totalDistance > 0, and strategy = 'nearest-neighbour'
        assert 'stops' in result, "Result should contain 'stops' key"
        assert len(result['stops']) > 0, "Result should have at least one stop"
        assert result['totalDistance'] >0, "Total distance should be greater than 0"
        assert result['strategy'] == 'nearest-neighbour', "Strategy should be 'nearest-neighbour'"

    def test_empty_matches_returns_empty_route(self):
        """Should return an empty route for empty matches"""

        # Arrange: Create an empty array of matches
        matches = []
        # Act: Call self.strategy.optimise([])
        result = self.strategy.optimise(matches)

        # Assert: Verify the result has empty stops and totalDistance = 0
        assert 'stops' in result, "Result should contain 'stops' key"
        assert len(result['stops']) == 0, "Stops should be empty"
        assert result['totalDistance'] == 0, "Total distance should be 0"
        assert result['strategy'] == 'nearest-neighbour', "Strategy should be 'nearest-neighbour'"

    def test_single_match_returns_zero_distance(self):
        """Should return zero distance for a single match"""

        # Arrange: Create an array with a single match
        matches = [
                    {
                        "id": "match-1",
                        "homeTeam": {
                            "id": "team-mexico",
                            "name": "Mexico",
                            "code": "MEX",
                            "group": "A"
                            },
                        "awayTeam": {
                            "id": "team-south-africa",
                            "name": "South Africa",
                            "code": "RSA",
                            "group": "A"
                            },
                        "city": {
                            "id": "city-mexico-city",
                            "name": "Mexico City",
                            "country": "Mexico",
                            "latitude": 19.3029,
                            "longitude": -99.1505,
                            "stadium": "Estadio Azteca",
                            "accommodationPerNight": 110.0
                            },
                        "kickoff": "2026-06-11T17:00:00Z",
                        "group": "A",
                        "matchDay": 1,
                        "ticketPrice": 120.0
                    }
        ]

        # Act: Call self.strategy.optimise(matches)
        result = self.strategy.optimise(matches)

        # Assert: Verify totalDistance = 0 and len(stops) = 1
        assert 'stops' in result, "Result should contain 'stops' key"
        assert len(result['stops']) == 1, "Result should have only one stop"
        assert result['totalDistance'] == 0, "Total distance should be 0"
        assert result['strategy'] == 'nearest-neighbour', "Strategy should be 'nearest-neighbour'"
