from flask import Flask, render_template, jsonify, request, g, session
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from transit import get_gtfs_data
from transit import get_real_time_data_request_response
from transit import get_bus_list
from transit import get_all_current_position_markers
from transit import get_route_data
from transit import get_trip_ids
from transit import list_of_closest_buses

import requests
import json
from collections import namedtuple
import datetime
import os
import pandas as pd

from helper import merge_two_dicts

DEFAULT_LOCATION = {u'lat': 39.7433814, u'lng': -104.98910989999999}
UTC_OFFSET = int(os.getenv('OFFSET', 7))

app = Flask(__name__, template_folder="./templates",
        static_url_path="/static",
        static_folder="./static")

@app.route("/api/trip_id/<trip_id>")
def trip_info(trip_id):
    data = get_route_data(trip_id)
    return(json.dumps(data))

@app.route("/api/route/")
def bus_info():
    route = request.args.get('route')
    route_id = route.split(':')[0].strip()
    trip_headsign = route.split(':')[1].strip()
    data = get_trip_ids(route_id, trip_headsign)
    return(json.dumps(data))

@app.route("/api/proximity/")
def near_me():

    lat = request.args.get('lat')
    lng = request.args.get('lng')

    if lat is None or lng is None:
        all_buses_df = pd.read_csv('trips.txt')
        return json.dumps(get_bus_list(all_buses_df))

    return(json.dumps(list_of_closest_buses(float(lat), float(lng))))


@app.route("/")
def mapview():
    get_gtfs_data()
    headers = get_real_time_data_request_response(header=True)
    last_modified = headers['Last-Modified']

    dt = datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
    dt = dt - datetime.timedelta(hours=UTC_OFFSET)
    last_modified = dt.strftime('%a, %d %b %Y %H:%M:%S MST')

    return render_template('map.html', last_modified=last_modified, json_api_key=os.getenv('JSON_API'))

if __name__ == "__main__":
    app.secret_key = os.getenv('SECRET_KEY', 'SECRET_KEY')
    app.debug = os.getenv('DEBUG', False)
    app.threaded = os.getenv('THREADED', False)
    app.run()
