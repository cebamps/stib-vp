from flask import (Flask, jsonify, g)
from stib_api import StibClient
from .services import Gtfs, VehicleCoordinates
import os


app = Flask(__name__)

app.config.update(dict(
    STIB_BASE=None,
    STIB_CLIENT_ID='xxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    STIB_CLIENT_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    DEFAULT_LINES=['1', '5', '2', '6', '3', '7'],
))

app.config.from_envvar('STIBVP_SETTINGS')

app.gtfs = Gtfs(os.path.join(app.root_path, 'gtfs.zip'))


def get_stib_api():
    if not hasattr(g, 'stib_api'):
        g.stib_api = StibClient(
            base=app.config['STIB_BASE'],
            client_id=app.config['STIB_CLIENT_ID'],
            client_secret=app.config['STIB_CLIENT_SECRET'],
        )
    return g.stib_api


@app.route('/env')
def envprint():
    import os
    return jsonify(dict(os.environ))


@app.route('/test.json')
def route_test():
    api = get_stib_api()
    vc = VehicleCoordinates(api=api, gtfs=app.gtfs)
    gjson = vc.get_coordinates_geojson(app.config['DEFAULT_LINES'])
    # Geojson is a subclass of dict, so we can directly encode it using jsonify
    return jsonify(gjson)
