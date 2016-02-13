from __future__ import print_function
from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
from io import BytesIO
import zipfile
import os
import os.path
import datetime

UTC_OFFSET = int(os.getenv('OFFSET', 7))
DEFAULT_LOCATION = {u'lat': 39.7433814, u'lng': -104.98910989999999}

def get_gtfs_data(force=False):
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
                print("File are not the same, submit rerequest")
                if force:
                    rerequest=True
            else:
                print("File unchanged!")
                if not os.path.isfile('stops.txt') or not os.path.isfile('trips.txt'):
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

def get_markers_for_list_entities(list_entities, stops_df, current_location=DEFAULT_LOCATION, trips_df=None):
    if trips_df is None:
        trips_df = pd.read_csv('trips.txt')

    marker = []
    for entity in list_entities:
        stop_time_update = entity.trip_update.stop_time_update[0]
        delay = stop_time_update.departure.delay
        uncertainty = stop_time_update.departure.uncertainty
        dt = datetime.datetime.fromtimestamp(stop_time_update.departure.time)
        dt = dt - datetime.timedelta(hours=UTC_OFFSET)
        departure_time = dt.strftime('%H:%M')

        closest_stop_time = 0
        closest_stop_name = ''

        trip_id = entity.trip_update.trip.trip_id
        route_id, route_name = get_bus_name(trip_id, trips_df)

        lat, lon, stop_name = get_location_of_stop_time_update(stop_time_update)

        marker.append((lat, lon, stop_name, departure_time, delay, uncertainty, closest_stop_time, closest_stop_name, route_id, route_name, trip_id))

    return marker

def get_location_of_stop_time_update(stop_time_update):
    stops_df = pd.read_csv('stops.txt')
    lat = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lat'].iloc[0]
    lon = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_lon'].iloc[0]
    stop_name = stops_df[stops_df['stop_id']==int(stop_time_update.stop_id)]['stop_name'].iloc[0].replace('[ X Stop ]', '')
    return lat, lon, stop_name


def get_stop_location_list(stop_time_update):
    list_stop_location = []

    for stop_time in stop_time_update:
        lat, lon, stop_name = get_location_of_stop_time_update(stop_time)
        list_stop_location.append({'lat': lat, 'lng': lon})

    return list_stop_location

def get_closest_stop_time(closest_stop_id, entity):

    for stop_time_update in entity.trip_update.stop_time_update:
        if int(stop_time_update.stop_id) == int(closest_stop_id):
            dt = datetime.datetime.fromtimestamp(stop_time_update.departure.time)
            dt = dt - datetime.timedelta(hours=UTC_OFFSET)
            departure_time = dt.strftime('%H:%M')
            return(departure_time)

def get_stop_name(stop_id, stops_df):
    return(stops_df.loc[stops_df['stop_id'] == 10277]['stop_name'].values[0])

def find_closest_stop(stops_df, latlon, stop_id_list):
    lat = latlon[0]
    lon = latlon[1]
    stops_df = stops_df[stops_df['stop_id'].isin(stop_id_list)]
    stops_df['minimum_distance'] = (stops_df['stop_lat'] - lat)**2 + (stops_df['stop_lon'] - lon)**2
    
    closest_stop_id = stops_df.loc[stops_df['minimum_distance'].argmin()]['stop_id']
    
    return closest_stop_id

def get_bus_name(trip_id, trips_df):
    return(trips_df[trips_df['trip_id'] == int(trip_id)]['route_id'].values[0],
            trips_df[trips_df['trip_id'] == int(trip_id)]['trip_headsign'].values[0])

def get_stop_id_list(entity):
    stop_id_list = []
    for sq in entity.trip_update.stop_time_update:
        stop_id_list.append(int(sq.stop_id))
    return stop_id_list

def get_bus_list(trips_df):
    dt = datetime.datetime.now()
    dt = dt - datetime.timedelta(hours=UTC_OFFSET)
    dt.isoweekday()

    saturday = dt.isoweekday() == 6
    sunday = dt.isoweekday() == 7

    if saturday:
        trips_df = trips_df[trips_df['service_id'] == 'SA']
    elif sunday:
        trips_df = trips_df[trips_df['service_id'] == 'SU']
    else: # weekday:
        trips_df = trips_df[trips_df['service_id'] == 'WK']

    trips_df['unique_route_id'] = 'Route ' + trips_df['route_id']+': '+trips_df['trip_headsign']
    bl = trips_df['unique_route_id'].unique()
    return(bl.tolist())


def get_location_of_routes(l):

    routePaths = {}
    for entity in l:
        trip_id = entity.trip_update.trip.trip_id
        routePaths[trip_id] = get_stop_location_list(entity.trip_update.stop_time_update)

    return routePaths

def get_all_current_position_markers(route, current_location=DEFAULT_LOCATION):
    stops_df = pd.read_csv('stops.txt')

    l = get_currently_active_trips(route)
    markers = {route: get_markers_for_list_entities(l,  stops_df, current_location)}
    routePaths = get_location_of_routes(l)

    data = {'markers': markers,
            'routePaths': routePaths }

    return(data)

def parse_route_name(route):
    route_id = route.split(':')[0].replace('Route ', '').strip(' ')
    trip_headsign = route.split(':')[1].strip(' ')
    
    return route_id, trip_headsign

def get_trip_id(route, trips_df):
    dt = datetime.datetime.now()
    dt = dt - datetime.timedelta(hours=UTC_OFFSET)
    dt.isoweekday()

    saturday = dt.isoweekday() == 6
    sunday = dt.isoweekday() == 7

    if saturday:
        trips_df = trips_df[trips_df['service_id'] == 'SA']
    elif sunday:
        trips_df = trips_df[trips_df['service_id'] == 'SU']
    else: # weekday:
        trips_df = trips_df[trips_df['service_id'] == 'WK']

    trips_df['unique_route_id'] = 'Route ' + trips_df['route_id']+': '+trips_df['trip_headsign']
    route_id, trip_headsign = parse_route_name(route)
    trips_df = trips_df[trips_df['route_id'] == route_id]
    trips_df = trips_df[trips_df['trip_headsign'] == trip_headsign]
    return trips_df['trip_id'].tolist()

def get_currently_active_trips(route):
    trips_df = pd.read_csv('trips.txt')
    total_trip_list = [str(item) for item in get_trip_id(route, trips_df)]
    return get_entities(total_trip_list)
