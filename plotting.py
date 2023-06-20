import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime


drone_folder = './experiment_data/'
optitrack_folder = '~/repos/python_natnet/experiment_data/'

drone_file = drone_folder + 'Wed_Jun_14_17:03:57_2023' + '/data.csv'
optitrack_file = optitrack_folder + 'Wed_Jun_14_17:03:42_2023' + '/data.csv'

drone_data = pd.read_csv(drone_file)
optitrack_data = pd.read_csv(optitrack_file)

m1_data = np.array(drone_data['motor.m1'].tolist())
m2_data = np.array(drone_data['motor.m2'].tolist())
m3_data = np.array(drone_data['motor.m3'].tolist())
m4_data = np.array(drone_data['motor.m4'].tolist())
thrust_data = np.array(drone_data['stabilizer.thrust'].tolist())

posx_data = np.array(optitrack_data['Pos x'].tolist())
posy_data = np.array(optitrack_data['Pos y'].tolist())
posz_data = np.array(optitrack_data['Pos z'].tolist())
quat1_data = np.array(optitrack_data['Rot 1'].tolist())
quat2_data = np.array(optitrack_data['Rot 2'].tolist())
quat3_data = np.array(optitrack_data['Rot 3'].tolist())
quat4_data = np.array(optitrack_data['Rot 4'].tolist())

drone_time_data = np.array(drone_data['Time'].tolist())
opti_time_data = np.array(optitrack_data['Time'].tolist())



def plot_trajectory():
    ax = plt.axes(projection='3d')
    ax.plot3D(posx_data, posz_data, posy_data) # ground is xz-plane, y is up
    plt.show()


def plot_time_comp():
    global drone_time_data
    global opti_time_data
    drone_time_data = abs(drone_time_data - 1686762000)
    opti_time_data = abs(opti_time_data - 1686762000)

    plt.subplot(2, 1, 1)
    plt.plot(drone_time_data, thrust_data, 'ko-')
    plt.title('')
    plt.ylabel('Drone thrust')
    plt.xlabel('Time from drone')

    plt.subplot(2, 1, 2)
    plt.plot(opti_time_data, posy_data, 'r.-')
    plt.ylabel('Optitrack y-data')
    plt.xlabel('Time from optitrack')

    plt.show()


# Find time stamp at which first motor is turned on (thrust can take values between 10001 and 60000)
# start_time_idx = np.argmax(thrust_data > 10001)
# start_time = drone_time_data[start_time_idx]
# # Print as human friendly timestamp to sanity check
# print(start_time)
# print(datetime.datetime.fromtimestamp(start_time).strftime('%c'))

# plot_time_comp()


thrust_df = pd.DataFrame({'Times': drone_data['Time'], 'thrusts': drone_data['stabilizer.thrust']})
posy_df = pd.DataFrame({'Times': optitrack_data['Time'], 'y-pos': optitrack_data['Pos y']})

combine_df = pd.merge_asof(posy_df, thrust_df, on='Times', tolerance=1.0)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#     print(combine_df)


fig, ax1 = plt.subplots(figsize=(9, 6))
ax2 = ax1.twinx()  

ax1.plot(combine_df['Times'], combine_df['thrusts'], color='r', label='Drone thrust')
ax2.plot(combine_df['Times'], combine_df['y-pos'], color='b', label='y-position from OptiTrack')

lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)

plt.show()




