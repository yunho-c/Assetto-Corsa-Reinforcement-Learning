# %%
import gym
from acenv_1 import AssettoCorsaEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import os

# %% [markdown]a
# # 2. Load Environment

# %%
env = AssettoCorsaEnv()
env = DummyVecEnv([lambda: env]) # The algorithms require a vectorized environment to run <- comment from copilot, damn!
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./tensorboard/")

# %%
# episodes = 1000
# for episode in range(1, episodes+1):
#     state = env.reset()
#     done = False
#     score = 0

#     while not done:
#         # env.render()
#         action = env.action_space.sample()
#         n_state, reward, done, info = env.step(action)
#         score += reward
#     print('Episode:{} Score:{}'.format(episode, score))
# # env.close()

# %% [markdown]
# # 3. Train

# %%
PPO_Path = os.path.join('Training', 'Saved Models', 'PPO_Model_AssettoCorsa')
for i in range(4):
    model.learn(total_timesteps=7200)
    model.save(PPO_Path)
