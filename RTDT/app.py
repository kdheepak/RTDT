from flask import Flask, render_template, jsonify, request, g, session
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from transit import get_gtfs_data
from transit import get_real_time_data_request_response
from transit import get_bus_list
from transit import get_all_current_position_markers

import requests
import json
from collections import namedtuple
import datetime
import os
import pandas as pd

from helper import merge_two_dicts

DEFAULT_LOCATION = {u'lat': 39.7433814, u'lng': -104.98910989999999}

app = Flask(__name__, template_folder="./templates")
GoogleMaps(app)

@app.route("/bus/", defaults={'route_number': None, 'route_name': None} )
@app.route("/bus/<route_number>/<route_name>")
def bus_info(route_number, route_name):
    data = {
            'route': {'number': route_number, 
                    'name': route_name}
            }
    return(json.dumps(data))

@app.route("/")
def mapview():
    return render_template('map.html', json_api_key=os.getenv('JSON_API'))

if __name__ == "__main__":
    app.secret_key = os.getenv('SECRET_KEY', 'SECRET_KEY')
    app.debug = os.getenv('DEBUG', False)
    app.threaded = os.getenv('THREADED', False)
    app.run()
