import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 002 fine
# 003 fine
# 004 not so good
# 005 fine
# 006 fine kinda noisy at each end
# 007 not so good
# 008 fine
# 009 fine

# trajectory_data = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_009.csv', skiprows=6)

# print(trajectory_data)

# x = trajectory_data['PX']
# y = trajectory_data['PZ']
# z = trajectory_data['PY']


# # 3D plot
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(x, y, z)
# ax.set_xlabel('X [m]')
# ax.set_ylabel('Y [m]')
# ax.set_zlabel('Z [m]')
# ax.set_title('Drone flight trajectory')
# plt.show()

trajectory_data2 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_002.csv', skiprows=6)
trajectory_data3 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_003.csv', skiprows=6)
trajectory_data5 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_005.csv', skiprows=6)
trajectory_data6 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_006.csv', skiprows=6)
trajectory_data8 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_008.csv', skiprows=6)
trajectory_data9 = pd.read_csv('~/Downloads/Take-2023-07-31-09.55.10-AM_009.csv', skiprows=6)

time2 = trajectory_data2['Time (Seconds)'].to_numpy()
x2 = trajectory_data2['PX'].to_numpy()
y2 = trajectory_data2['PZ'].to_numpy()
z2 = trajectory_data2['PY'].to_numpy()
# Find index at which z2 > 0
start_idx2 = np.where(z2 > 0.0001)[0][0]
z2 = z2[start_idx2:]
time2 = time2[start_idx2:] - time2[start_idx2]

time3 = trajectory_data3['Time (Seconds)']
x3 = trajectory_data3['PX']
y3 = trajectory_data3['PZ']
z3 = trajectory_data3['PY']
start_idx3 = np.where(z3 > 0.0001)[0][0]
z3 = z3[start_idx3:]
time3 = time3[start_idx3:] - time3[start_idx3]


time5 = trajectory_data5['Time (Seconds)']
x5 = trajectory_data5['PX']
y5 = trajectory_data5['PZ']
z5 = trajectory_data5['PY']
start_idx5 = np.where(z5 > 0.0001)[0][0]
z5 = z5[start_idx5:]
time5 = time5[start_idx5:] - time5[start_idx5]

time6 = trajectory_data6['Time (Seconds)']
x6 = trajectory_data6['PX']
y6 = trajectory_data6['PZ']
z6 = trajectory_data6['PY']
start_idx6 = np.where(z6 > 0.0001)[0][0]
z6 = z6[start_idx6:]
time6 = time6[start_idx6:] - time6[start_idx6]

time8 = trajectory_data8['Time (Seconds)']
x8 = trajectory_data8['PX']
y8 = trajectory_data8['PZ']
z8 = trajectory_data8['PY']
start_idx8 = np.where(z8 > 0.0027)[0][0]
z8 = z8[start_idx8:]
time8 = time8[start_idx8:] - time8[start_idx8]

time9 = trajectory_data9['Time (Seconds)']
x9 = trajectory_data9['PX']
y9 = trajectory_data9['PZ']
z9 = trajectory_data9['PY']
start_idx9 = np.where(z9 > 0.0001)[0][0]
z9 = z9[start_idx9:]
time9 = time9[start_idx9:] - time9[start_idx9]



fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(time2, z2, label='002')
# ax.plot(time3, z3, label='003')
ax.plot(time5, z5, label='005')
ax.plot(time6, z6, label='006')
# ax.plot(time8, z8, label='008')
ax.plot(time9, z9, label='009')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Z [m]')
ax.set_title('Drone flight trajectory')
plt.show()