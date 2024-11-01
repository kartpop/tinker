prompt_dev = """

You are an AI assistant that generates Python scripts using Matplotlib to create diagrams illustrating science concepts.

You may be doing this task for the first time or as a redo based on feedback. 

Your output should be a json object with the following keys:
{
    "plan": "Your pseudocode plan or your steps to improve the diagram based on feedback.",
    "code": "Your Python code to generate the diagram.",
}

If you are doing this task for the first time:

- **Analyze** the text and identify key concepts that can be visually represented.
    - **Concepts**: The text will contain scientific concepts.
- **Scientific Accuracy**: Ensure the diagram is scientifically accurate and correctly represents the concepts.
- **Easy Digestion**: Make the diagram easy to understand and digest, ensuring that the key concepts are clearly communicated.
- **Plan** step-by-step what to include in the diagram, and write this plan in pseudocode with great detail.


If you are doing this task as a REDO:

- **Thoroughly review** your previous work and the subsequent feedback before proceeding.
    - You have access to your previously generated code, the resulting image and the feedback provided.
- **Aim to improve your performance** based on the feedback provided. Specifically, focus on the following:
    - **Scientific Accuracy**: Ensure the diagram accurately represents the scientific concept.
    - **Clarity**: Make the diagram as clear and easy to understand as possible. Consider labels, colors, and other visual elements.
    - **Adhere to Feedback**: If feedback exists in previous chat completion messages, adhere to the feedback strictly.


For both FIRST TIMERS and REDOERS:

- **Assume** that the following imports have been made:
        `import matplotlib.pyplot as plt
        import numpy as np`
- **Code output** the complete Python code in a single code block.

Your code should be complete and runnable as-is to generate the diagram.

Adhere STRICTLY to the output format specified:
{
    "plan": "...",
    "code": "...",
}

"""

prompt_qa = """

You are an AI assistant that critiques Matplotlib diagrams, especially those illustrating STEM concepts.

Your task is as follows:

1. **Analyze** the diagram provided.
2. **Identify** flaws in the diagram. Flaws can be both:
    - **Visual**: Issues with clarity, labeling, aesthetics, color choices, or any elements that may cause confusion or misinterpretation.
    - **Conceptual**: Errors in the representation of the underlying STEM concepts, inaccuracies in the data, or misinterpretations of the scientific principles.
3. **Provide a detailed critique**:
    - **Visual Flaws**: Describe each visual flaw clearly and suggest specific improvements.
    - **Conceptual Flaws**: Pinpoint exact conceptual faults, explain why they are incorrect, and provide step-by-step instructions to resolve them.
4. **If the diagram is correct** and has no flaws, state that it is correct.
5. **If the diagram is incorrect** or can be improved, provide clear, detailed, and actionable instructions for improving the diagram. These instructions should include:
    - Specific changes to the visual elements (e.g., labels, colors, line styles).
    - Corrections to the conceptual representation (e.g., correct formulas, accurate data representation).
    - If necessary, suggest completely redoing the work with a new approach or diagram.
6. **Ensure clarity and precision**: Your critique should be easy to understand and implement, with no ambiguity.

Adhere STRICTLY to the output format specified:
{
    "correct": true/false, # true if the diagram is correct, false otherwise
    "feedback": "...",
}

"""

concept = """**Lift**: This is the force that allows planes to rise off the ground. It's generated 
by the wings of the plane. Imagine a bird flapping its wings. As air flows over and under the wings, 
it creates a difference in air pressure. The shape of the wing (called an airfoil) is designed so 
that air moves faster over the top of the wing than underneath it. According to Bernoulli's principle, 
the faster air on top creates a lower pressure compared to the higher pressure underneath. This 
pressure difference creates lift, allowing the plane to ascend."""

import datetime
import json
import base64
import requests
from openai import OpenAI
import os
import matplotlib.pyplot as plt
import numpy as np

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_matplotlib_diagram(concept: str, max_turns: int = 5) -> str:
    client = OpenAI()
    history = []
    folder_id = 'e28f1763-04f0-4e93-8153-691c67eb9180'  # Replace with your folder ID
    sub_folder = datetime.datetime.now().strftime("%d-%b-%Y-%H%M%S")
    folder = "diagrams"  
    
    # Create folder and sub_folder if they do not exist
    if not os.path.exists(folder):
        os.mkdir(folder)

    sub_folder_path = os.path.join(folder, sub_folder)
    if not os.path.exists(sub_folder_path):
        os.mkdir(sub_folder_path)

    for i in range(max_turns):
        # Generate diagram
        concept_message = {
            "role": "user",
            "content": concept
        }
        history.append(concept_message)

        messages = [{"role": "system", "content": prompt_dev}] + history

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace with the correct engine name
            n=1,
            stop=None,
            temperature=0.7,
            messages=messages,
        )

        generated_diagram_message = response.choices[0].message
        history.append(
            json.loads(generated_diagram_message.model_dump_json())
        )  # to avoid OpenAI types (?)

        try:
            response_data = json.loads(generated_diagram_message.content)
            plan = response_data.get("plan", "")
            code = response_data.get("code", "")
        except json.JSONDecodeError:
            print("Error decoding JSON from LLM response.")
            print("Response content:", generated_diagram_message.content)
            break

        # Log the plan (you can modify this as needed)
        print(f"Plan for {i}: {plan}\n")

        # Execute the generated code to create the diagram
        try:
            exec(code, globals())
        except Exception as e:
            print(f"Error executing generated code: {e}")
            break
        
        image_filename = f"diagram_{i}"
        image_path = os.path.join(sub_folder_path, image_filename)
        
        plt.savefig(image_path, format='png', dpi=300, bbox_inches='tight')
        base64_image = encode_image(f"{image_path}.png")

        # Upload the image to GoFile
        # upload_response = requests.post(
        #     "https://store6.gofile.io/uploadFile",
        #     files={"file": open(image_path, "rb")},
        #     data={"folderId": folder_id}
        # )

        # if upload_response.status_code == 200:
        #     try:
        #         link = upload_response.json()["data"]["downloadPage"]
        #     except (json.JSONDecodeError, KeyError):
        #         print("Error parsing upload response.")
        #         print("Response content:", upload_response.text)
        #         break
        # else:
        #     print(f"Failed to upload file. Status code: {upload_response.status_code}")
        #     print("Response content:", upload_response.text)
        #     break

        # Append messages with the image
        # tool_message = {
        #     "role": "tool",
        #     "content": "This tool created an image which is encapsulated in the following 'user' message",
        # }
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "This is the diagram generated after execution of the code generated by the AI assistant.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            ],
        }
        # history.append(tool_message)
        history.append(user_message)

        # Get feedback
        feedback_messages = [{"role": "system", "content": prompt_qa}] + history

        feedback_response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace with the correct engine name
            n=1,
            temperature=0.7,
            messages=feedback_messages,
        )

        feedback_message = feedback_response.choices[0].message

        try:
            feedback = json.loads(feedback_message.model_dump_json())
            history.append(feedback)
        except json.JSONDecodeError:
            history.append({"role": "assistant", "content": feedback_message.content})

        # Check if the diagram is correct
        if feedback.get("correct", False):
            print("Diagram is correct.")
            return image_path

    print("Maximum iterations reached.")
    return image_path