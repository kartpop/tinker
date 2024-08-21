import { useEffect, useState } from "react";

type message = {
  src: string;
  text: string;
};

export default function Argonk() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<message[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080/ws");

    ws.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.onmessage = (event) => {
      console.log("Received data:", event.data);
      setMessages((prevMessages) => [
        ...prevMessages,
        { src: "agent", text: event.data },
      ]);
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
      setMessages((prevMessages) => [
        ...prevMessages,
        { src: "user", text: prompt },
      ]);
      socket.send(prompt);
      setPrompt("");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-grow overflow-y-auto">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-4 m-4 ${
              message.src === "user"
                ? "w-4/5 ml-auto bg-orange-200 rounded-lg"
                : ""
            }`}
          >
            <p className="text-gray-800" style={{ wordWrap: "break-word" }}>
              {message.text}
            </p>
          </div>
        ))}
      </div>
      <div className="flex-shrink-0 flex items-center m-2">
        <textarea
          rows={1}
          value={prompt}
          onChange={handlePromptChange}
          className="w-full p-2 border-2 border-gray-300 focus:border-orange-300 focus:outline-none resize-none h-auto max-h-36 overflow-y-auto"
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
