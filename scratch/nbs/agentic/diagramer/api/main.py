import os
import json
import datetime
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI

# Import prompts from the new directory
from prompts.development_prompt import DEVELOPMENT_PROMPT
from prompts.qa_prompt import QA_PROMPT

app = FastAPI()

# Initialize OpenAI client (ensure you have set the OPENAI_API_KEY environment variable)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=5)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

class DiagramRequest(BaseModel):
    concept: str
    client_id: str

class DiagramResponse(BaseModel):
    detail: str

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.post("/generate-diagram", response_model=DiagramResponse, status_code=202)
async def generate_diagram(request: DiagramRequest, background_tasks: BackgroundTasks):
    client_id = request.client_id
    concept = request.concept

    if client_id not in manager.active_connections:
        raise HTTPException(status_code=400, detail="WebSocket connection not found for the given client_id.")

    background_tasks.add_task(process_and_notify, client_id, concept)
    return DiagramResponse(detail="Diagram generation started. You will be notified via WebSocket once it's ready.")

def encode_image(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""

def execute_generate_diagram(concept: str, max_turns: int = 5):
    """
    Synchronously execute the diagram generation process.
    This function is intended to be run in a separate thread.
    """
    try:
        image_path, prompt_tokens, completion_tokens, total_tokens = generate_matplotlib_diagram(concept, max_turns)
        return {
            "image_path": image_path,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    except Exception as e:
        return {"error": str(e)}

async def process_and_notify(client_id: str, concept: str):
    loop = asyncio.get_event_loop()
    try:
        # Run the blocking diagram generation in a thread pool
        result = await loop.run_in_executor(executor, execute_generate_diagram, concept, 5)

        if "error" in result:
            message = json.dumps({"error": result["error"]})
            await manager.send_message(client_id, message)
            return

        image_path = result["image_path"]
        prompt_tokens = result["prompt_tokens"]
        completion_tokens = result["completion_tokens"]
        total_tokens = result["total_tokens"]

        # Encode image to base64
        base64_image = encode_image(image_path)
        if not base64_image:
            await manager.send_message(client_id, json.dumps({"error": "Failed to encode image."}))
            return

        message = {
            "image_path": image_path,
            "base64_image": f"data:image/png;base64,{base64_image}",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

        await manager.send_message(client_id, json.dumps(message))
    except Exception as e:
        error_message = {"error": str(e)}
        await manager.send_message(client_id, json.dumps(error_message))

def generate_matplotlib_diagram(concept: str, max_turns: int = 5):
    history = []
    concept_message = {"role": "user", "content": concept}

    sub_folder = datetime.datetime.now().strftime("%d-%b-%Y-%H%M%S")
    folder = "/aux/src/tinker/scratch/nbs/agentic/diagramer/diagrams"
    sub_folder_path = os.path.join(folder, sub_folder)
    os.makedirs(sub_folder_path, exist_ok=True)

    history = []
    prompt_dev_message = {"role": "system", "content": DEVELOPMENT_PROMPT}
    concept_message = {"role": "user", "content": concept}
    
    prompt_tokens, completion_tokens, total_tokens = 0, 0, 0

    try:
        for i in range(max_turns):
            # Step 1: Generate Diagram
            messages = [prompt_dev_message, concept_message] + history

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Replace with the correct engine name
                n=1,
                temperature=0.7,
                messages=messages,
            )

            generated_diagram_message = response.choices[0].message
            plot_code_message = {"role": "assistant", "content": generated_diagram_message.content}
            history = [plot_code_message]

            try:
                response_data = json.loads(generated_diagram_message.content)
                plan = response_data.get("plan", "")
                code = response_data.get("code", "")
            except json.JSONDecodeError:
                print("Error decoding JSON from LLM response.")
                print("Response content:", generated_diagram_message.content)
                break

            # Log the plan and code
            print(f"Plan for iteration {i}:\n{plan}\n")
            print(f"Code for iteration {i}:\n{code}\n")

            # Execute the generated code to create the diagram
            try:
                exec(code, globals())
            except Exception as e:
                print(f"Error executing generated code:\n\ncode:\n{code}\n\nerror:\n{e}")
                user_message = {
                    "role": "user",
                    "content": f"Error executing generated code, please fix the code:\n{e}",
                }
                history.append(user_message)
                continue

            image_filename = f"diagram_{i}.png"
            image_path = os.path.join(sub_folder_path, image_filename)

            try:
                plt.savefig(image_path, format="png", dpi=300, bbox_inches="tight")
                plt.close()  # Close the plot to free memory
            except Exception as e:
                print(f"Error saving the diagram: {e}")
                break

            base64_image = encode_image(image_path)

            user_image_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the diagram generated after execution of the code generated by the AI assistant.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            }
            history.append(user_image_message)

            # Step 2: Get Feedback
            feedback_messages = [prompt_qa_message := {"role": "system", "content": QA_PROMPT}, concept_message] + history

            feedback_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Replace with the correct engine name
                n=1,
                temperature=0.7,
                messages=feedback_messages,
            )
            
            prompt_tokens += feedback_response.usage.prompt_tokens
            completion_tokens += feedback_response.usage.completion_tokens
            total_tokens += feedback_response.usage.total_tokens

            feedback = feedback_response.choices[0].message
            feedback_message = {"role": "assistant", "content": feedback.content}

            print(f"Feedback received: {feedback.content}\n")

            try:
                history = [plot_code_message, user_image_message, feedback_message]
                feedback_content = json.loads(feedback.content)
                if feedback_content.get("correct", False):
                    print("Diagram is correct.")
                    return image_path, prompt_tokens, completion_tokens, total_tokens
            except json.JSONDecodeError:
                history.append({"role": "assistant", "content": feedback.content})

    except Exception as e:
        print(f"Error occurred during diagram generation: {e}")
        return "No image generated.", prompt_tokens, completion_tokens, total_tokens
    finally:
        log_path = os.path.join(sub_folder_path, "log.json")
        try:
            with open(log_path, "w") as log_file:
                json.dump(history, log_file, indent=4)
            print(f"Log saved at: {log_path}")
        except Exception as e:
            print(f"Failed to save log: {e}")

    print("Maximum iterations reached.")
    image_path = image_path if 'image_path' in locals() else "No image generated."
    return image_path, prompt_tokens, completion_tokens, total_tokens

# def main():
#     concept_text = """Planes fly through a combination of four fundamental forces: lift, weight (gravity), thrust, and drag. Let's break this down into smaller parts to understand how each of these forces works together to get a plane airborne:

#     1. **Lift**: This is the force that allows planes to rise off the ground. It's generated by the wings of the plane. Imagine a bird flapping its wings. As air flows over and under the wings, it creates a difference in air pressure. The shape of the wing (called an airfoil) is designed so that air moves faster over the top of the wing than underneath it. According to Bernoulli's principle, the faster air on top creates a lower pressure compared to the higher pressure underneath. This pressure difference creates lift, allowing the plane to ascend.

#     2. **Weight (Gravity)**: Weight is the force acting downwards due to gravity. It pulls the plane towards the Earth. For a plane to take off, the lift generated must be greater than the weight of the plane in order to rise into the sky.

#     3. **Thrust**: This is the force that propels the plane forward. It is produced by the plane's engines. You can think of thrust as the car's accelerator. Just like stepping on the gas makes a car go forward, the engines generate thrust, pushing the plane ahead. The more powerful the engines, the greater the thrust.

#     4. **Drag**: This is the resistance the plane faces as it moves through the air, similar to how you feel resistance when you put your hand out of a moving car's window. Drag works against the thrust, trying to slow the plane down. Aircraft designers work hard to create shapes that minimize drag, making it easier for planes to fly.

#     When you put it all together: during takeoff, the engines generate thrust, pushing the plane down the runway. As speed increases, the wings generate lift. Once lift surpasses weight, the plane rises into the sky. While in flight, thrust keeps the plane moving forward, while lift works to keep it up, with drag and weight constantly pulling back."""

#     image_path, prompt_tokens, completion_tokens, total_tokens = generate_matplotlib_diagram(concept_text)
#     print(f"Diagram saved at: {image_path}")
#     print(f"Prompt tokens: {prompt_tokens}")
#     print(f"Completion tokens: {completion_tokens}")
#     print(f"Total tokens: {total_tokens}")

# if __name__ == "__main__":
#     main()