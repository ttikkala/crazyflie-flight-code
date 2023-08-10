import pandas as pd
import matplotlib.pyplot as plt


# Plot rewards
losses = pd.read_csv('losses-Mon-Aug--7-21:44:06-2023.csv')



plt.plot(losses['Training step'], losses['Q1 Predictions Mean'])
plt.show()


