from flask import (
    Flask, request, redirect, jsonify, g, render_template, url_for,
    make_response
)
from stib_api import StibClient
from .services import Gtfs, VehicleCoordinates
from .settings import Configuration
import os


app = Flask(__name__)

app.config.from_object(Configuration)

app.gtfs = Gtfs(os.path.join(app.root_path, 'gtfs.zip'))


def get_stib_api():
    if not hasattr(g, 'stib_api'):
        g.stib_api = StibClient(
            base=app.config['STIB_BASE'],
            client_id=app.config['STIB_CLIENT_ID'],
            client_secret=app.config['STIB_CLIENT_SECRET'],
        )
    return g.stib_api


@app.route('/api/positions')
def positions():
    lines = request.args.get('lines', '').split(',')
    api = get_stib_api()
    vc = VehicleCoordinates(api=api, gtfs=app.gtfs)
    gjson = vc.get_coordinates_geojson(lines)
    # Geojson is a subclass of dict, so we can directly encode it using jsonify
    return jsonify(gjson)


@app.route('/colors.css')
def colors_css():
    resp = make_response(render_template('colors.css', routes=app.gtfs.routes))
    # Attribute of werkzeug.wrappers.Response inherited from
    # werkzeug.wrappers.CommonResponseDescriptorsMixin
    resp.mimetype = 'text/css'
    return resp


@app.route('/')
def show_map():
    shown_routes = request.args.get('lines')
    if not shown_routes:
        shown_routes = ','.join(app.config['DEFAULT_ROUTES'])
        return redirect(url_for('show_map', lines=shown_routes))

    shown_routes = shown_routes.split(',')
    return render_template(
        'map.html',
        shown_routes=shown_routes,
        routes=app.gtfs.routes,
    )
