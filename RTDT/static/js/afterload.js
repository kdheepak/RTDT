
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

var temp = null

function onLocationFound(e) {
    var radius = e.accuracy / 2;
    // L.marker(e.latlng).addTo(map);

$.ajax({
  url: "/api/proximity/",
  type: "get", //send it through get method
  dataType: 'json',
  data:{lat:e.latlng.lat, lng:e.latlng.lng},
  success: function(d) {
    console.log(d)
    temp = d
    select = document.getElementById('routename');
    var opt = document.createElement('option');
    opt.value = "None"
    opt.innerHTML = "------ SELECT ROUTE -----";
    select.appendChild(opt);
    for (var i = 0, length = d.length; i < length; i++){
        var opt = document.createElement('option');
                opt.value = d[i];
                opt.innerHTML = d[i];
                select.appendChild(opt);
    }
    opt.value = "None"
    opt.innerHTML = "------ ALL ROUTES -----";
    select.appendChild(opt);
    addAllBus()
  },
  error: function(xhr) {
    select = document.getElementById('routename');
    var opt = document.createElement('option');
    opt.value = "None"
    opt.innerHTML = "------ SELECT ROUTE -----";
    select.appendChild(opt);
    addAllBus()
  }
});

}

function onLocationError(e) {
    select = document.getElementById('routename');
    var opt = document.createElement('option');
    opt.value = "None"
    opt.innerHTML = "------ SELECT ROUTE -----";
    select.appendChild(opt);
    addAllBus()
}

function addAllBus() {
$.ajax({
  url: "/api/proximity/",
  type: "get", //send it through get method
  dataType: 'json',
  success: function(d) {
    console.log(d)
    select = document.getElementById('routename');
    for (var i = 0, length = d.length; i < length; i++){
        var opt = document.createElement('option');
                opt.value = d[i];
                opt.innerHTML = d[i];
                select.appendChild(opt);
    }
   document.getElementById('spinnerElement').style.display = 'none';
  },
  error: function(xhr) {
      console.log(xhr)
  }
});

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
var routeMarkerList = Array();
var markerList = Array();
var polyline = null

function drawRoute(trip_id) {

    console.log(markerList)

    removeMarkers()

    console.log(trip_id)

    d3.json("/api/trip_id/"+trip_id,function(error,response){

        json_data = response

        for (var i = 0; i < json_data.stop_time_update.length; i++) {

            marker = new L.marker([json_data.stop_time_update[i].location[0],
                    json_data.stop_time_update[i].location[1]])
                .bindPopup("<b>" + json_data.stop_time_update[i].stop_name + "</b><br>Expected departure time - " +
                        json_data.stop_time_update[i].departure.time)
                .addTo(map);
            
        //Get latlng from first marker
        latlngs.push(marker.getLatLng());
        markerList.push(marker)
        }

    //You can just keep adding markers

    //From documentation http://leafletjs.com/reference.html#polyline
    // create a red polyline from an arrays of LatLng points
    polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
    markerList.push(polyline)
    // zoom the map to the polyline
    // map.fitBounds(polyline.getBounds());

    });

}

function removeMarkers() {
    for (var i = 0; i < markerList.length; i++) {
        map.removeLayer(markerList[i])
    }
    markerList.splice(0)
    latlngs.splice(0)
}

function removeRouteMarkers() {

    for (var i = 0; i < routeMarkerList.length; i++) {
        map.removeLayer(routeMarkerList[i])
    }
    routeMarkerList.splice(0)

}


function updateData(sel) {

    removeRouteMarkers()

    console.log(sel.value)

$.ajax({
  url: "/api/route/",
  type: "get", //send it through get method
  dataType: 'json',
  data:{route:sel.value},
  success: function(data) {
    console.log(data)

    removeMarkers()

    transitIcon = L.icon({
    iconUrl: '/static/transit.jpg',
    iconSize:     [25, 25], // size of the icon
    })
    for (var i = 0; i < data.length; i++) {

        marker = new L.marker([data[i].location[0],
                data[i].location[1]], {icon: transitIcon, trip_id: data[i].trip_id})
            .bindPopup("<b>" + data[i].trip_name + "</b><br>Expected to depart "+
                    data[i].current_location +
                    " at " +
                    data[i].expected_departure)
            .addTo(map);

        marker.on('click', function(e) {
            drawRoute(this.options.trip_id)
        })

    routeMarkerList.push(marker)
    }
  },
  error: function(xhr) {
    //Do Something to handle error
  }
});

}
