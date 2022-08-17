from stable_baselines3.common.env_checker import check_env
from acenv_1 import AssettoCorsaEnv

acenv = AssettoCorsaEnv()

print(check_env(acenv))