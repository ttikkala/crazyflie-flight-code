import pandas as pd
import matplotlib.pyplot as plt


# Plot rewards
rewards = pd.read_csv('rewards-no-vel.csv')
rewards = rewards.to_numpy()
# rewards *= 100000000

plt.hist(rewards)
plt.xscale('log')
plt.show()


