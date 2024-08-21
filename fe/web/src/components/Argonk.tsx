import { useEffect, useState } from "react";

export default function Argonk() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [prompt, setPrompt] = useState("");
  // const [messages, setMessages] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080/ws");

    ws.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.onmessage = (event) => {
      console.log("Received data:", event.data);
      // setMessages((prevMessages) => [...prevMessages, event.data]);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const handlePromptChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    const textarea = event.target;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
    setPrompt(textarea.value);
  };

  const handleSendPrompt = () => {
    if (socket && prompt !== "") {
      socket.send(prompt);
      setPrompt("");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-grow overflow-y-auto">
        <div className="w-4/5 bg-orange-300 rounded-lg p-4 m-4 ml-auto">
          <p className="text-gray-800">
            A prompt which is very long. Tell me something about the Amazon
            rainforest. What percentage of it lies in Brazil. Access detailed
            rooftop data based on Google's expansive mapping and computing
            resources to help estimate renewable rooftop solar energy potential
            and savings.
          </p>
        </div>

        <div className="p-4 m-4">
          <p className="text-gray-800">
            A prompt which is very long. Tell me something about the Amazon
            rainforest. What percentage of it lies in Brazil. Access detailed
            rooftop data based on Google's expansive mapping and computing
            resources to help estimate renewable rooftop solar energy potential
            and savings.
          </p>
        </div>

        <div className="w-4/5 bg-orange-300 rounded-lg p-4 m-4 ml-auto">
          <p className="text-gray-800">
            A prompt which is very long. Tell me something about the Amazon
            rainforest. What percentage of it lies in Brazil. Access detailed
            rooftop data based on Google's expansive mapping and computing
            resources to help estimate renewable rooftop solar energy potential
            and savings.
          </p>
        </div>

        <div className="w-4/5 bg-orange-300 rounded-lg p-4 m-4 ml-auto">
          <p className="text-gray-800">
            A prompt which is very long. Tell me something about the Amazon
            rainforest. What percentage of it lies in Brazil. Access detailed
            rooftop data based on Google's expansive mapping and computing
            resources to help estimate renewable rooftop solar energy potential
            and savings.
          </p>
        </div>

        <div className="p-4 m-4">
          <p className="text-gray-800">
            A prompt which is very long. Tell me something about the Amazon
            rainforest. What percentage of it lies in Brazil. Access detailed
            rooftop data based on Google's expansive mapping and computing
            resources to help estimate renewable rooftop solar energy potential
            and savings.
          </p>
        </div>
      </div>
      <div className="flex-shrink-0 flex items-center">
        <textarea
          rows={1}
          value={prompt}
          onChange={handlePromptChange}
          className="w-full p-2 border-2 bg-orange-50 border-gray-300 focus:border-orange-500 focus:outline-none resize-none h-auto max-h-36 overflow-y-auto"
          placeholder="Type a message..."
          style={{ height: "auto" }}
        />
        <img
          src="/up-arrow-png-20.png"
          alt="Send prompt"
          className="w-9 h-9 ml-2 cursor-pointer"
          onClick={handleSendPrompt}
        />
      </div>
    </div>
  );
}
