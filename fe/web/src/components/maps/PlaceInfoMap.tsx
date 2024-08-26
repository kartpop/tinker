"use client";

import {
  AdvancedMarker,
  APIProvider,
  InfoWindow,
  Map,
  Pin,
} from "@vis.gl/react-google-maps";
import { useEffect, useState } from "react";

export default function PlaceInfoMap() {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const position = { lat: 12.9716, lng: 77.5946 };

  const [openInfoWindow, setOpenInfoWindow] = useState(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [response, setResponse] = useState("");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080/ws");

    ws.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.onmessage = (event) => {
      console.log("Received message from backend:", event.data);
      setResponse(event.data);
      setOpenInfoWindow(true);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  if (!apiKey) {
    return <div>Error: Google Maps API key is missing</div>;
  }

  const handleAdvancedMarkerClick = (position: {
    lat: number;
    lng: number;
  }) => {
    console.log("Marker clicked", position);

    socket?.send(`Tell me something about lat: ${position.lat}, lng: ${position.lng}. Keep the response to maximum of 100 words. 
      Don't mention the lat and lng in the answer, but instead start the response 
      with "This place is <whatever-the-place-is>". After that continue with the information about that place.`);
  };

  const handleInfoWindowClose = () => {
    setOpenInfoWindow(false);
    setResponse("");
  };

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
            onClick={() => handleAdvancedMarkerClick(position)}
          >
            <Pin background={"darkorange"} borderColor={"darkorange"}>
              {openInfoWindow && (
                <InfoWindow
                  position={position}
                  onClose={() => handleInfoWindowClose()}
                >
                  <p>{response}</p>
                </InfoWindow>
              )}
            </Pin>
          </AdvancedMarker>
        </Map>
      </div>
    </APIProvider>
  );
}
