



// initialize the map
var map = L.map('map').setView([39.73, -104.99], 13);

L.tileLayer('https://{s}.tiles.mapbox.com/v4/{mapId}/{z}/{x}/{y}.png?access_token={token}', {
    attribution: '<a href="https://www.mapbox.com/about/maps/" target="_blank">&copy; Mapbox &copy; OpenStreetMap</a>',
    subdomains: ['a','b','c','d'],
    mapId: 'mapbox.emerald',
    token: 'pk.eyJ1Ijoia2RoZWVwYWs4OSIsImEiOiJjaWt2MXVtMHYwMGRydWFtM2JneDJ1MWMxIn0._Vr6g3q4myFgjWPB21SGiQ'
}).addTo(map);

	/* Initialize the SVG layer */
	map._initPathRoot()    

function onLocationFound(e) {
    var radius = e.accuracy / 2;
    L.marker(e.latlng).addTo(map);
}

function onLocationError(e) {
    alert(e.message);
}

map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);

map.locate({setView: true, maxZoom: 14});

// when view changes

function onViewChange(e) {
   $(".viewChangeClass").show(); 
}

map.on('move', function (e) { onViewChange(e) });

var json_data = null;

var latlngs = Array();

function drawRoute(trip_id) {

    d3.json("/api/"+trip_id,function(error,response){

        json_data = response

        for (var i = 0; i < json_data.stop_time_update.length; i++) {

            marker = new L.marker([json_data.stop_time_update[i].location[0],
                    json_data.stop_time_update[i].location[1]])
                .bindPopup(json_data.stop_time_update[i].stop_name)
                .addTo(map);
            
        //Get latlng from first marker
        latlngs.push(marker.getLatLng());

        }

    //You can just keep adding markers

    //From documentation http://leafletjs.com/reference.html#polyline
    // create a red polyline from an arrays of LatLng points
    var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);

    // zoom the map to the polyline
    // map.fitBounds(polyline.getBounds());

    });

}
