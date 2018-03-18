from contextlib import contextmanager
from csv import DictReader
from io import TextIOWrapper
from zipfile import ZipFile
import geojson


class Gtfs:
    def __init__(self, path):
        self.path = path
        self.stations = self._get_stations()
        self.routes = self._get_routes()

    def _get_stations(self):
        with self._file_iterator('stops.txt') as gtfs_stops:
            return {s['stop_id']: (float(s['stop_lon']), float(s['stop_lat']))
                    for s in gtfs_stops}

    def _get_routes(self):
        with self._file_iterator('routes.txt') as gtfs_routes:
            return {
                r['route_short_name']: {
                    key: r[key]
                    for key in ('route_long_name', 'route_color')
                }
                for r in gtfs_routes
            }

    @contextmanager
    def _file_iterator(self, name):
        """DictReader iterator for a file in the gtfs archive"""
        gtfs_zip = ZipFile(self.path)
        with TextIOWrapper(gtfs_zip.open(name), encoding='utf8') as gtfs_csv:
            yield DictReader(gtfs_csv)


class VehicleCoordinates:
    def __init__(self, api, gtfs):
        self.api = api
        self.gtfs = gtfs

    def get_coordinates(self, vehicles):
        """Dict mapping route ids to a list of lon-lat tuples"""
        positions = self.api.get_vehicle_positions(vehicles)
        coords = {
            l['lineId']: [
                self.gtfs.stations[v['pointId']]
                for v in l['vehiclePositions']
                if v['pointId'] in self.gtfs.stations
            ]
            for l in positions['lines']
        }
        return coords

    def get_coordinates_geojson(self, vehicles):
        """Returns a geojson object representing the vehicle positions.

        The object is a FeatureCollection containing MultiPoint
        Features with a "lineId" property for the route name.
        """
        vehicle_coords = self.get_coordinates(vehicles)
        features = [
            self._make_multipoint(vehicle, coords)
            for vehicle, coords in vehicle_coords.items()
        ]
        return geojson.FeatureCollection(features)

    def _make_multipoint(self, vehicle, coords):
        return geojson.Feature(
            geometry=geojson.MultiPoint(coords),
            properties={
                "lineId": vehicle,
                "marker-color": "#{}".format(self.gtfs.routes[vehicle]['route_color']),
            }
        )
