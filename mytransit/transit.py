from google.transit import gtfs_realtime_pb2

import requests
import pandas as pd
from io import BytesIO
import zipfile
import os

def get_gtfs_data():
    url = 'http://www.rtd-denver.com/GoogleFeeder/google_transit_Jan16_Runboard.zip'
    request = requests.get(url)
    z = zipfile.ZipFile(BytesIO(request.content))
    z.extractall()
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


def get_entities(bus_list):

    feed = gtfs_realtime_pb2.FeedMessage()

    r = requests.get('http://www.rtd-denver.com/google_sync/TripUpdate.pb', auth=(os.getenv('RTD_USERNAME'), os.getenv('RTD_PASSWORD')))

    feed.ParseFromString(r.content)

    list_entities = []

    for entity in feed.entity:
        if entity.trip_update.trip.trip_id in bus_list:
            list_entities.append(entity)

    return(list_entities)

def get_markers_for_list_entities(list_entities, stops_df):
    marker = []
    for entity in list_entities:
        stop_time_update = entity.trip_update.stop_time_update[0]
        lat = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lat'].iloc[0]
        lon = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lon'].iloc[0]
        marker.append((lat, lon))

    return marker

def main():

    bus20_east_df, bus20_west_df = get_bus_data_from_csv()

    bus20_east_list = convert_df_to_list(bus20_east_df)

