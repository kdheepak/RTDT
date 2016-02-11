from flask import Flask, render_template, jsonify, request
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from transit import get_bus_data_from_csv
from transit import convert_df_to_list
from transit import get_entities
from transit import get_gtfs_data
from transit import get_markers_for_list_entities
from transit import get_real_time_data_request_response

import json
from collections import namedtuple
import datetime
import os

from helper import merge_two_dicts

app = Flask(__name__, template_folder="./templates")
GoogleMaps(app)

@app.route("/data")
def data():

    print("before gtfs - {}".format(datetime.datetime.now()))
    get_gtfs_data()
    print("after gtfs - {}".format(datetime.datetime.now()))

    print("before csv - {}".format(datetime.datetime.now()))
    bus20_east_df, bus20_west_df, stops_df = get_bus_data_from_csv()
    print("after csv - {}".format(datetime.datetime.now()))

    print("before list - {}".format(datetime.datetime.now()))
    bus20_east_list = convert_df_to_list(bus20_east_df)
    bus20_west_list = convert_df_to_list(bus20_west_df)
    print("after list - {}".format(datetime.datetime.now()))

    print("before header - {}".format(datetime.datetime.now()))
    headers = get_real_time_data_request_response(header=True)
    last_modified = headers['Last-Modified']
    print("after header - {}".format(datetime.datetime.now()))

    print("before entities - {}".format(datetime.datetime.now()))
    l1 = get_entities(bus20_east_list)
    l2 = get_entities(bus20_west_list)
    print("after entities - {}".format(datetime.datetime.now()))

    bus_20_east_dict = {'/static/transit-east.png': get_markers_for_list_entities(l1, stops_df),
               }
    bus_20_west_dict = {'/static/transit-west.png': get_markers_for_list_entities(l2, stops_df),
                 }

    markers = merge_two_dicts(bus_20_east_dict, bus_20_west_dict)

    lat_lng = {'lat': 39.7392, 'lng': -104.9903} # Denver downtown

    UTC_OFFSET = 7

    dt = datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
    dt = dt - datetime.timedelta(hours=UTC_OFFSET)
    last_modified = dt.strftime('%a, %d %b %Y %H:%M:%S MST')

    data = {'last_modified': last_modified,
            'location': lat_lng,
            'markers': markers}

    # data = {"last_modified": "Wed, 10 Feb 2016 20:13:39 MST", "location": {"lat": 39.7434915, "lng": -104.9890398}, "markers": {"/static/transit-west.png": [], "/static/transit-east.png": [[39.7434915, -104.9890398]]}}

    return json.dumps(data)

@app.route("/")
def mapview():
    # creating a map in the view

    return render_template('map.html', json_api_key=os.getenv('JSON_API'))

if __name__ == "__main__":
    app.debug = os.getenv('DEBUG', False)
    app.threaded = os.getenv('THREADED', False)
    app.run()
