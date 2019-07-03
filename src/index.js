import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

var map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  maxZoom: 18,
  id: 'mapbox.streets',
  accessToken: process.env.MAPBOX_ACCESS_TOKEN,
}).addTo(map);

fetch('api/geo.json', {
  accept: 'application/json',
  credentials: 'same-origin',
}).then((response) => {
  if (response.status == 403) {
    window.location.pathname = 'auth/recurse';
  } else {
    return response.json();
  }
}).then((responseJson) => {
  var markers = L.markerClusterGroup();
  var layer = L.geoJSON(responseJson, {
    pointToLayer: function(geoJsonPoint, latlng) {
      var image = geoJsonPoint['properties']['image_url'];
      return L.marker(latlng, {
        icon: L.icon({iconUrl: image, iconSize: [32, 32]}),
        title: geoJsonPoint['properties']['name'],
      }).bindPopup(`
        <section>
          <div><img src="${image}"/></div>
          <p><a href="${geoJsonPoint['properties']['directory_url']}">
            ${geoJsonPoint['properties']['name']}
          </a></p>
          <p>${geoJsonPoint['properties']['location_name']}</p>
        </section>
      `);
    }
  });
  markers.addLayer(layer);
  map.addLayer(markers);
});
