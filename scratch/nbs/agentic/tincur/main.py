from nbs.agentic.lib.swarm.repl import run_demo_loop
from nbs.agentic.curio_v0.agents import curio
import time

if __name__ == "__main__":
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_to_write = f"nbs/agentic/tincur/output/{timestamp}.txt"
    run_demo_loop(curio, debug=True, file_to_write=file_to_write)
