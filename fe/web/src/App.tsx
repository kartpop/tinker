import Argonk from "./components/Argonk";
import Knogra from "./components/Knogra";

function App() {
  return (
    <div className="flex h-full overflow-hidden">
      <div className="w-2/3 bg-orange-400 h-screen">
        <Knogra />
      </div>
      <div className="w-1/3 bg-orange-200 h-screen">
        <Argonk />
      </div>
    </div>
  );
}

export default App;
