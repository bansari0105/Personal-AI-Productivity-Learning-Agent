import gym
from gym import spaces
import numpy as np
from collections import deque

class ProductivityEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()

        # 🔹 Continuous action: intensity [0, 1]
        self.action_space = spaces.Box(
            low=0.0, high=1.0, shape=(1,), dtype=np.float32
        )

        # 🔹 State: energy, avg_reward, total_productivity
        self.observation_space = spaces.Box(
            low=0.0, high=1000.0, shape=(3,), dtype=np.float32
        )

        # Internal state
        self.energy = 50.0
        self.steps = 0

        # 🧠 Long-term memory
        self.reward_memory = deque(maxlen=10)
        self.total_productivity = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.energy = 50.0
        self.steps = 0
        self.reward_memory.clear()
        self.total_productivity = 0.0

        state = np.array([self.energy, 0.0, 0.0], dtype=np.float32)
        return state, {}

    def step(self, action):
        self.steps += 1

        intensity = float(action[0])  # 0 → rest, 1 → deep work
        reward = intensity * 2.0

        self.energy += reward
        self.reward_memory.append(reward)
        self.total_productivity += reward

        avg_reward = (
            np.mean(self.reward_memory)
            if len(self.reward_memory) > 0 else 0.0
        )

        state = np.array(
            [self.energy, avg_reward, self.total_productivity],
            dtype=np.float32
        )

        terminated = self.steps >= 20
        truncated = False

        return state, reward, terminated, truncated, {}
