"use client";

import { APIProvider, Map } from "@vis.gl/react-google-maps";

export default function Knogra() {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const position = { lat: 12.9716, lng: 77.5946 };

  if (!apiKey) {
    return <div>Error: Google Maps API key is missing</div>;
  }

  return (
    <APIProvider apiKey={apiKey}>
      <div className="h-screen">
        <Map center={position} zoom={9} />
      </div>
    </APIProvider>
  );
}
