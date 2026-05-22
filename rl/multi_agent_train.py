"""Multi-agent training (experimental/placeholder for Phase 2).

Future work: Train specialized RL agents per task type.
For now, this is a template/placeholder.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from prod_env.productivity_env import ProductivityEnv

AGENT_NAMES = ["work", "learn", "health"]

def main():
    env = ProductivityEnv()
    agents = {}

    for name in AGENT_NAMES:
        agents[name] = PPO(
            "MlpPolicy",
            env,
            verbose=1
        )

    os.makedirs("models", exist_ok=True)

    for name, agent in agents.items():
        print(f"\n[{name.upper()}] Training agent...")
        agent.learn(total_timesteps=5_000)
        agent.save(f"models/{name}_agent")
        print(f"[{name.upper()}] Saved to models/{name}_agent.zip")

    print("\n[Multi-Agent] All agents trained.")

if __name__ == "__main__":
    main()
