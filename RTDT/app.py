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

@app.route("/update")
def update():
    get_gtfs_data(force=True)
    return("Update complete")

@app.route("/data")
def data():

    print(request.args)

    data_info = request.args.get('info', None)

    if data_info == 'bus_list':
        get_gtfs_data()
        all_buses_df = pd.read_csv('trips.txt')
        return json.dumps({'bus_list': get_bus_list(all_buses_df)})

    if data_info == 'set_position':
        print('inside set_position')
        current_location = json.loads(request.args.get('data'))
        # session['current_location'] = current_location
        return(json.dumps({'position': current_location}))

    if data_info == 'request':
        route = request.args.get('data')
        print(route)
        current_location = DEFAULT_LOCATION
        data = get_all_current_position_markers(route, current_location)
        print(data)
        data['routes'] = [route]
        return(json.dumps(data))


@app.route("/")
def mapview():
    # creating a map in the view

    headers = get_real_time_data_request_response(header=True)
    last_modified = headers['Last-Modified']

    UTC_OFFSET = 7
    dt = datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
    dt = dt - datetime.timedelta(hours=UTC_OFFSET)
    last_modified = dt.strftime('%a, %d %b %Y %H:%M:%S MST')

    return render_template('map.html', last_modified=last_modified, json_api_key=os.getenv('JSON_API'))

if __name__ == "__main__":
    app.secret_key = os.getenv('SECRET_KEY', 'SECRET_KEY')
    app.debug = os.getenv('DEBUG', False)
    app.threaded = os.getenv('THREADED', False)
    app.run()
