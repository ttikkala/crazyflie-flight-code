# Plot rewards.csv
import pandas as pd


import matplotlib.pyplot as plt




# Plot rewards.csv
rewards = pd.read_csv('rewards.csv')
rewards = rewards.to_numpy()

plt.plot(rewards)
plt.show()