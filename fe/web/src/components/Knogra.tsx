import PlaceInfoMap from "./maps/PlaceInfoMap";

export default function Knogra() {
  const displayGoogleMaps = import.meta.env.VITE_DISPLAY_GOOGLE_MAPS === "true";

  console.log("displayGoogleMaps", displayGoogleMaps);

  if (!displayGoogleMaps) {
    return <div>Knogra</div>;
  }

  return <PlaceInfoMap></PlaceInfoMap>;
}
