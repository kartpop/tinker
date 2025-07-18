import json
import os
import asyncio

from nbs.agentic.lib.swarm import Swarm
from nbs.agentic.lib.swarm.util import debug_print


async def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    async for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # End of response message
            content = ""

        if "response" in chunk:
            return chunk["response"]


def pretty_print_messages(messages, file_to_write=None) -> None:
    for message in messages:
        # Log messages to file
        if file_to_write:
            os.makedirs(os.path.dirname(file_to_write), exist_ok=True)
            with open(file_to_write, "a") as f:
                sender = message["role"]
                content = message["content"]
                f.write(f"{sender}: {content}\n\n")

        if message["role"] != "assistant":
            continue

        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


async def run_demo_loop(
    starting_agent,
    context_variables=None,
    stream=False,
    debug=False,
    file_to_write=None,
) -> None:
    client = Swarm()
    print("Starting Swarm CLI 🐝")

    messages = []
    agent = starting_agent

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        if stream:
            response = client.run(
                agent=agent,
                messages=messages,
                context_variables=context_variables or {},
                stream=stream,
                debug=debug,
            )
            response = await process_and_print_streaming_response(response)
        else:
            response = await client.run(
                agent=agent,
                messages=messages,
                context_variables=context_variables or {},
                stream=stream,
                debug=debug,
            )
            pretty_print_messages(response.messages, file_to_write)

        messages.extend(response.messages)
        agent = response.agent
