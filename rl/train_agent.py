import sys
import os

# Add parent directory to path so we can import prod_env and other modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from prod_env.productivity_env import ProductivityEnv

def main():
    env = ProductivityEnv()

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        gamma=0.99
    )

    print("[Training] Starting PPO training for 10,000 timesteps...")
    model.learn(total_timesteps=10_000)

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    model.save("models/productivity_agent")

    print("[Training] Done. Model saved to models/productivity_agent.zip")

if __name__ == "__main__":
    main()
