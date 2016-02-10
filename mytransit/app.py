from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from transit import get_bus_data_from_csv
from transit import convert_df_to_list
from transit import get_entities
from transit import get_gtfs_data
from transit import get_markers_for_list_entities

from helper import merge_two_dicts

app = Flask(__name__, template_folder="./templates")
GoogleMaps(app)

@app.route("/")
def mapview():
    # creating a map in the view
    
    get_gtfs_data()

    bus20_east_df, bus20_west_df, stops_df = get_bus_data_from_csv()

    bus20_east_list = convert_df_to_list(bus20_east_df)
    bus20_west_list = convert_df_to_list(bus20_west_df)

    l1 = get_entities(bus20_east_list)
    l2 = get_entities(bus20_west_list)

    bus_20_east_dict = {'http://maps.google.com/mapfiles/ms/icons/green-dot.png': get_markers_for_list_entities(l1, stops_df),
                 }
    bus_20_west_dict = {'http://maps.google.com/mapfiles/ms/icons/blue-dot.png': get_markers_for_list_entities(l2, stops_df),
                 }

    markers = merge_two_dicts(bus_20_east_dict, bus_20_west_dict)

    mymap = Map(
        identifier="view-side",
        lat=39.7392,
        lng=-104.9903,
        markers=markers
    )
    return render_template('map.html', mymap=mymap)

if __name__ == "__main__":
    app.debug = True
