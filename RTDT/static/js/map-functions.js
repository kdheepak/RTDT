// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see the error "The Geolocation service
// failed.", it means you probably did not give permission for the browser to
// locate you.

var map = null
var pos = null
var myPos = null

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: new google.maps.LatLng(39.7392, -104.9903),
    zoom: 15,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });

  // Try HTML5 geolocation.
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      map.setCenter(pos);
        myPos = new google.maps.LatLng(pos['lat'], pos['lng']);
        latLng = new google.maps.LatLng(pos['lat'], pos['lng']);
        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
            animation: google.maps.Animation.DROP,
            opacity: 1,
            optimized: false,
        });
      console.log("init_complete")
        $(document).trigger('init_complete');
    }, function() {
      handleLocationError(true);
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false);
  }

}

function handleLocationError(browserHasGeolocation) {
    console.log(browserHasGeolocation)
        render()
}



var data = []
var gmarkers = [];
var intervalNumber = 0;
var firstUpdate = 1;
var removemarkerslist = [];

function render()
    {
        console.log('Finding positions')
        console.log(pos)

        $.getJSON('/data',{
        info: 'set_position',
        data: JSON.stringify(pos)
      } )
       
    }

function getInfoCallback(map, content) {
    var infowindow = new google.maps.InfoWindow({content: content});
    return function() {
            infowindow.setContent(content);
            infowindow.open(map, this);
        };
}


function removeMarkers(removemarkerslist) {
    for(var i = 0; i < removemarkerslist.length; i++) {
        removemarkerslist[i].setMap(null);
    }
}

function drawRoute(route, bounds){
    var image = {
        url: '/static/transit.jpg',
        // This marker is 20 pixels wide by 32 pixels high.
        // size: new google.maps.Size(20, 32),
        // The origin for this image is (0, 0).
        origin: new google.maps.Point(0, 0),
        // The anchor for this image is the base of the flagpole at (0, 32).
        anchor: new google.maps.Point(0, 32),
        scaledSize: new google.maps.Size(25, 25)
      };
      // Shapes define the clickable region of the icon. The type defines an HTML
      // <area> element 'poly' which traces out a polygon as a series of X,Y points.
      // The final coordinate closes the poly by connecting to the first coordinate.
      var shape = {
        coords: [1, 1, 1, 20, 18, 20, 18, 1],
        type: 'poly'
      };

    for (var i = 0, length = data.markers[route].length; i < length; i++) {

        var stop_data = data.markers[route][i];

        console.log(stop_data);

        var contentString = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<h3 id="firstHeading" class="firstHeading">'+ stop_data[8] + ' ' + stop_data[9] + ' </h3>'+
      '<div id="bodyContent">'+
      'Expected to depart <b>'+
      stop_data[2]+
      '</b> at <b>'+
      stop_data[3]+
      // '</b>.'+
      // '.<br>Expected to depart <b>'+
      // stop_data[7]+
      // '</b> at <b>'+
      // stop_data[6]+
      '</b>.';
      if(stop_data[4] !== 0) {
        contentString = contentString + '<br>Delay - '+
      stop_data[4]+
      '<br>Uncertainty - '+
      stop_data[5];
        }
        contentString = contentString+
      '</p>'+
      '</div>'+
      '</div>';

        latLng = new google.maps.LatLng(stop_data[0], stop_data[1]);
        bounds.extend(latLng);
        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
            icon: image,
            opacity: 1,
            optimized: false,
        });
        // getInfoCallback(map, contentString)();
        google.maps.event.addListener(marker, 'click',
                getInfoCallback(map, contentString, stop_data[10]));

        gmarkers.push(marker);

        // Add path


    };
}

function plotPath(trip_id) {
         var routePlanCoordinates = data.routePaths[trip_id]

             console.log(routePlanCoordinates)

     for (var i = 0, length = routePlanCoordinates.length; i < length; i++) {

         latLng = new google.maps.LatLng(routePlanCoordinates[i]['lat'],
                routePlanCoordinates[i]['lng']);

        var contentString = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<div id="bodyContent">'+
      'Expected to depart <b>'+
      routePlanCoordinates[i]['stop_name']+
      '</b> at <b>'+
      routePlanCoordinates[i]['departure_time']+
      '</b>.';
      '</p>'+
      '</div>'+
      '</div>';

        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
           icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 0.5,
            fillColor: '#ff0000',
            strokeOpacity: 1.0,
            strokeColor: '#fff000',
            strokeWeight: 3.0,
            scale: 5 //pixels
          }   ,
            opacity: 1,
            optimized: false,
        });
        google.maps.event.addListener(marker, 'click',
                getInfoCallbackRoute(map, contentString )
                );


     }


           var routePath = new google.maps.Polyline({
             path: routePlanCoordinates,
             geodesic: true,
             strokeColor: '#FF0000',
             strokeOpacity: 1.0,
             strokeWeight: 2
           });

           routePath.setMap(map);

    }

function continueRender()
    {
    var bounds = new google.maps.LatLngBounds();

    bounds.extend(myPos)

    for (var j = 0, jlength = data.routes.length; j < jlength; j++) {

        var route = data.routes[j];

        drawRoute(route, bounds)

        $(document).trigger('render_complete');

        if (firstUpdate == 1) {
            map.fitBounds(bounds);
            firstUpdate = 0
        }

    }

}


function getInfoCallbackRoute(map, content) {
    var infowindow = new google.maps.InfoWindow({content: content});
    return function() {
            infowindow.setContent(content);
            infowindow.open(map, this);
        };
}

function getInfoCallback(map, content, trip_id) {
    var infowindow = new google.maps.InfoWindow({content: content});
    return function() {
            infowindow.setContent(content);
            infowindow.open(map, this);
            plotPath(trip_id)
        };
}


function removebox() {

    var div = document.getElementById('loading');
    // hide
    div.style.visibility = 'hidden';
    // OR
    div.style.display = 'none';


}

$(document).bind('init_complete', render);
$(document).bind('render_complete', removebox);

$.getJSON('/data',{
info: 'bus_list'
} , function(d) {
    d
    select = document.getElementById('routename');

    var opt = document.createElement('option');
    opt.value = "None"
    opt.innerHTML = "------ SELECT ROUTE -----";
    select.appendChild(opt);

    for (var i = 0, length = d.bus_list.length; i < length; i++){
        var opt = document.createElement('option');
                opt.value = d.bus_list[i];
                opt.innerHTML = d.bus_list[i];
                select.appendChild(opt);
    }
})



function updateData(sel) {

    if (sel != "None") {
    firstUpdate = 1;
    getData(sel)
    // setInterval(function() { getTestData(sel); }, 10000);
    }

}

function getTestData(sel) {
data = {"routes": ["Route 0: Union Station"], "markers": {"Route 0: Union Station": []}}
}

function getData(sel) {
$.getJSON('/data',{
    info : 'request',
    data : sel.value
  }, function(d) {
            data = d
        })
.done(function( data ) {
        continueRender()
    });
}


