from __future__ import print_function
from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
from io import BytesIO
import zipfile
import os
import os.path
import datetime

def get_gtfs_data():
    url = 'http://www.rtd-denver.com/GoogleFeeder/google_transit_Jan16_Runboard.zip'
    headers_file = 'google_feeder_headers.txt'

    last_modified = requests.head(url).headers['Last-Modified']
    rerequest = False

    if not os.path.isfile(headers_file):
        rerequest = True
    else:
        with open(headers_file) as f:
            f_line = f.read()
            if last_modified not in f_line:
                print("File are not the same")
                rerequest = True
            else:
                print("File unchanged!")
                if not os.path.isfile('stops.txt'):
                    rerequest = True
                    print("Files missing")

    if rerequest:
        print("Re-requesting data")
        request = requests.get(url)
        z = zipfile.ZipFile(BytesIO(request.content))
        z.extractall()
        with open(headers_file, 'w') as f:
            print(last_modified, file=f)
        return z
                

def get_bus_data_from_csv():

    stops_df = pd.read_csv('stops.txt')
    trips_df = pd.read_csv('trips.txt')

    bus20_df = trips_df[trips_df['route_id']=='20']
    bus20_df = bus20_df[bus20_df['service_id']=='WK']

    bus20_east_df = bus20_df[bus20_df['trip_headsign']=='Anschutz Medical Campus']
    bus20_west_df = bus20_df[bus20_df['trip_headsign']=='Denver West']

    return(bus20_east_df, bus20_west_df, stops_df)

def convert_df_to_list(df):

    # bus20_east_list = [str(i) for i in bus20_east_df['trip_id'].tolist()]
    # bus20_west_list = [str(i) for i in bus20_west_df['trip_id'].tolist()]
    return([str(i) for i in df['trip_id'].tolist()])

def get_real_time_data_request_response(header=False):
    if header:
        r = requests.head('http://www.rtd-denver.com/google_sync/TripUpdate.pb', auth=(os.getenv('RTD_USERNAME'), os.getenv('RTD_PASSWORD')))
        return(r.headers)
    else:
        r = requests.get('http://www.rtd-denver.com/google_sync/TripUpdate.pb', auth=(os.getenv('RTD_USERNAME'), os.getenv('RTD_PASSWORD')))
        if r.ok:
            return(r.content)
        else:
            return None

def get_entities(bus_list):

    feed = gtfs_realtime_pb2.FeedMessage()

    content = get_real_time_data_request_response()

    feed.ParseFromString(content)

    list_entities = []

    for entity in feed.entity:
        if entity.trip_update.trip.trip_id in bus_list:
            list_entities.append(entity)

    return(list_entities)

def get_markers_for_list_entities(list_entities, stops_df):
    marker = []
    for entity in list_entities:
        stop_time_update = entity.trip_update.stop_time_update[0]
        delay = stop_time_update.departure.delay
        uncertainty = stop_time_update.departure.uncertainty
        UTC_OFFSET = 7
        dt = datetime.datetime.fromtimestamp(stop_time_update.departure.time)
        dt = dt - datetime.timedelta(hours=UTC_OFFSET)
        departure_time = dt.strftime('%H:%M')

        lat = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lat'].iloc[0]
        lon = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lon'].iloc[0]
        stop_name = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_name'].iloc[0].replace('[ X Stop ]', '')
        marker.append((lat, lon, stop_name, departure_time, delay, uncertainty))

    return marker

def main():
    pass
