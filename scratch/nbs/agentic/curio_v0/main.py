from nbs.agentic.lib.swarm.repl import run_demo_loop
from nbs.agentic.curio_v0.agents import curio

if __name__ == "__main__":
    run_demo_loop(curio, debug=True)
