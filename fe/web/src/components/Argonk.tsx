import { useState } from "react";

export default function Argonk() {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = event.target;
    // Reset the height
    textarea.style.height = "auto";
    // Adjust height based on scrollHeight
    textarea.style.height = `${textarea.scrollHeight}px`;
    setInputValue(textarea.value);
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
          value={inputValue}
          onChange={handleInputChange}
          className="w-full p-2 border-2 bg-orange-50 border-gray-300 focus:border-orange-500 focus:outline-none resize-none h-auto max-h-36 overflow-y-auto"
          placeholder="Type a message..."
          style={{ height: "auto" }}
        />
        <img
          src="/up-arrow-png-20.png"
          alt="Send message"
          className="w-9 h-9 ml-2 cursor-pointer"
        />
      </div>
    </div>
  );
}
