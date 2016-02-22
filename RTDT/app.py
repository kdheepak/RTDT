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
    return(json.dumps(list_of_closest_buses(float(lat), float(lng))))

@app.route("/")
def mapview():
    return render_template('map.html', json_api_key=os.getenv('JSON_API'))

if __name__ == "__main__":
    app.secret_key = os.getenv('SECRET_KEY', 'SECRET_KEY')
    app.debug = os.getenv('DEBUG', False)
    app.threaded = os.getenv('THREADED', False)
    app.run()
