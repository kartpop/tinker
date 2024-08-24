"use client";

import {
  AdvancedMarker,
  APIProvider,
  InfoWindow,
  Map,
  Pin,
} from "@vis.gl/react-google-maps";
import { useState } from "react";

export default function Knogra() {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const position = { lat: 12.9716, lng: 77.5946 };

  const [openInfoWindow, setOpenInfoWindow] = useState(false);

  if (!apiKey) {
    return <div>Error: Google Maps API key is missing</div>;
  }

  return (
    <APIProvider apiKey={apiKey}>
      <div className="h-screen">
        <Map
          center={position}
          zoom={9}
          mapId={import.meta.env.VITE_GOOGLE_MAPS_MAP_ID}
        >
          <AdvancedMarker
            position={position}
            onClick={() => setOpenInfoWindow(true)}
          >
            <Pin background={"darkorange"} borderColor={"darkorange"}>
              {openInfoWindow && (
                <InfoWindow
                  position={position}
                  onClose={() => setOpenInfoWindow(false)}
                >
                  <p>I'm in Bangalore</p>
                </InfoWindow>
              )}
            </Pin>
          </AdvancedMarker>
        </Map>
      </div>
    </APIProvider>
  );
}
