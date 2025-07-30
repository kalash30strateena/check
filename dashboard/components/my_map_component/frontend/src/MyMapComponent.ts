import React, { useEffect } from "react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const provincesGeoJSON = {/* ... your provinces GeoJSON ... */};
const geojsonData = {/* ... your stations GeoJSON ... */};

const MyMapComponent: React.FC = () => {
  useEffect(() => {
    // Create map
    const map = L.map("map").setView([-38.4161, -63.6167], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap",
      maxZoom: 18,
    }).addTo(map);

    // Add province markers
    provincesGeoJSON.features.forEach((feature: any) => {
      const coords = feature.geometry.coordinates[0];
      const lons = coords.map((c: any) => c[0]);
      const lats = coords.map((c: any) => c[1]);
      const centroid: [number, number] = [
        (Math.min(...lats) + Math.max(...lats)) / 2,
        (Math.min(...lons) + Math.max(...lons)) / 2,
      ];
      L.marker(centroid)
        .addTo(map)
        .bindTooltip(feature.properties.province, { direction: "top", permanent: false })
        .bindPopup(feature.properties.province);
    });

    // Add stations layer
    const stationsLayer = L.geoJSON(geojsonData, {
      pointToLayer: (feature: any, latlng: L.LatLng) => {
        const marker = L.marker(latlng)
          .bindTooltip(feature.properties.name, { permanent: false, direction: "top" })
          .bindPopup(feature.properties.name);

        marker.on("click", () => {
          // Send station name to Streamlit Python!
          Streamlit.setComponentValue(feature.properties.name);
        });

        return marker;
      },
    }).addTo(map);

    // Cleanup on unmount
    return () => {
      map.remove();
    };
  }, []);

  return (
    <div id="map" style={{ height: "600px", width: "100%" }} />
  );
};

export default withStreamlitConnection(MyMapComponent);
