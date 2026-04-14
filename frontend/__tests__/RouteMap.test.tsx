import { render, screen } from '@testing-library/react';
import RouteMap from '../src/components/RouteMap';
import { OptimisedRoute } from '../src/types';

// mock react-leaflet to avoid real map rendering, instead expose test IDs for assertions.
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }: any) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => null,
  Marker: ({ children }: any) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }: any) => <div>{children}</div>,
  Polyline: () => null,
  useMap: () => ({}),
}));

// factory function for a minimal City object- coordinates are fixed for these tests.
const mockCity = (id: string, name: string): City => ({
  id,
  name,
  country: 'USA',
  latitude: 40.7128,
  longitude: -74.006,
});

// factory for an ItineraryStop object- defaults allow tests to override only fields they care about.
const mockStop = (
  stopNumber: number,
  city: City,
  homeTeam = 'Home FC',
  awayTeam = 'Away United',
  kickoff = '2024-03-15T19:30:00Z'
): ItineraryStop => ({
  stopNumber,
  city,
  match: {
    homeTeam: { name: homeTeam },
    awayTeam: { name: awayTeam },
    kickoff,
  },
});

// Shared city fixture reused across multiple tests to avoid repetition.
const NEW_YORK = mockCity('nyc', 'New York');

describe('RouteMap', () => {
  // When route is null, the map should not render a placeholder message should be shown instead.
  it('should render placeholder message when route is null', () => {
    
    // Arrange
    render(<RouteMap route={null} originCity={null} />);

    // Assert: the placeholder fallback text should be visible in place of the map.
    expect(screen.getByText('Validate a route to see it displayed on the map.')).toBeInTheDocument();
  });


  // a valid route should switch the component from placeholder state to map view.
  it('should render a map container when route is provided', () => {
    const mockRoute: OptimisedRoute = {
      stops: [mockStop(1, NEW_YORK)],
      totalDistance: 0,
      strategy: 'nearest-neighbour',
      feasible: true,
      warnings: [],
      countriesVisited: ['USA'],
      missingCountries: [],
    };

    render(<RouteMap route={mockRoute} originCity={null} />);

    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });

  // Three distinct cities ensure all stops are iterated, not just the first or last.
  it('should render a marker for each stop in the route', () => {
    const CHICAGO = mockCity('chi', 'Chicago');
    const HOUSTON = mockCity('hou', 'Houston');

    const mockRoute: OptimisedRoute = {
      stops: [
        mockStop(1, NEW_YORK),
        mockStop(2, CHICAGO),
        mockStop(3, HOUSTON),
      ],
      totalDistance: 0,
      strategy: 'nearest-neighbour',
      feasible: true,
      warnings: [],
      countriesVisited: ['USA'],
      missingCountries: [],
    };

    render(<RouteMap route={mockRoute} originCity={null} />);

    expect(screen.getAllByTestId('marker')).toHaveLength(3);
  });
  
  // Empty stops is a valid degenerate state; map should mount but render no markers.
  it('should handle route with empty stops array', () => {
    const mockRoute: OptimisedRoute = {
      stops: [],
      totalDistance: 0,
      strategy: 'nearest-neighbour',
      feasible: true,
      warnings: [],
      countriesVisited: [],
      missingCountries: [],
    };

    render(<RouteMap route={mockRoute} originCity={null} />);

    expect(screen.getByTestId('map-container')).toBeInTheDocument();
    expect(screen.queryAllByTestId('marker')).toHaveLength(0);
  });
});
