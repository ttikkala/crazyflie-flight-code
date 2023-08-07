import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

trajectory_data = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_006.csv', skiprows=6)

print(trajectory_data)

x = trajectory_data['PX']
y = trajectory_data['PY']
z = trajectory_data['PZ']


# 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()