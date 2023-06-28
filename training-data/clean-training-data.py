import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
import sys

file_path = './Mon-Jun-26-12:58:51-2023/data.csv'
# file_path = str(sys.argv[1])


flight_data = pd.read_csv(file_path)

time = np.array(flight_data['Time'].tolist())

m1_data = np.array(flight_data['motor.m1'].tolist())
m2_data = np.array(flight_data['motor.m2'].tolist())
m3_data = np.array(flight_data['motor.m3'].tolist())
m4_data = np.array(flight_data['motor.m4'].tolist())

posx_data = np.array(flight_data['Pos x'].tolist())
posy_data = np.array(flight_data['Pos y'].tolist())
posz_data = np.array(flight_data['Pos z'].tolist())
quatw_data = np.array(flight_data['Quat 1'].tolist())
quatx_data = np.array(flight_data['Quat 2'].tolist())
quaty_data = np.array(flight_data['Quat 3'].tolist())
quatz_data = np.array(flight_data['Quat 4'].tolist())

start_time_idx = np.argmax(m1_data > 0)

time = time - time[start_time_idx]
time = time[start_time_idx:]

m1_data = m1_data[start_time_idx:]
m2_data = m2_data[start_time_idx:]
m3_data = m3_data[start_time_idx:]
m4_data = m4_data[start_time_idx:]

posx_data = posx_data[start_time_idx:]
posy_data = posy_data[start_time_idx:]
posz_data = posz_data[start_time_idx:]
quatw_data = quatw_data[start_time_idx:]
quatx_data = quatx_data[start_time_idx:]
quaty_data = quaty_data[start_time_idx:]
quatz_data = quatz_data[start_time_idx:]

v_x = np.gradient(posx_data, time)
v_y = np.gradient(posy_data, time)
v_z = np.gradient(posz_data, time)

# print(np.shape(v_x), np.shape(posx_data))



# plt.subplot(2, 1, 1)
# plt.plot(time, posx_data, 'ko-')
# plt.title('')
# plt.ylabel('Position in x')
# plt.xlabel('Time')

# plt.subplot(2, 1, 2)
# plt.plot(time, v_x, 'r.-')
# plt.ylabel('Velocity in x')
# plt.xlabel('Time')

# plt.show()




# output_file = "./data-clean-" + file_path[13:21] + ".csv"

# df = pd.DataFrame({'Time' : time, 'motor.m1' : m1_data, 'motor.m2' : m2_data, 'motor.m3' : m3_data, 'motor.m4' : m4_data, 
#                    'Pos x': posx_data, 'Pos y': posy_data, 'Pos z': posz_data, 
#                    'Vel x': v_x, 'Vel y': v_y, 'Vel z': v_z, 
#                    'Quat w': quatw_data, 'Quat x': quatx_data, 'Quat y': quaty_data, 'Quat z': quatz_data})
# df.to_csv(output_file, index=False)



### Transition data

state_data = np.column_stack((posx_data, posy_data, posz_data, v_x, v_y, v_z, quatw_data, quatx_data, quaty_data, quatz_data))
action_data = np.column_stack((m1_data, m2_data, m3_data, m4_data))

transitions = np.zeros(((np.shape(posx_data)[0] - 1), 24))
print(transitions)

print(state_data[0])
print(action_data[0])
print(state_data[1])


for i in range(np.shape(posx_data)[0] - 1):
    transitions[i][:10] = state_data[i]
    transitions[i][10:14] = action_data[i]
    transitions[i][14:] = state_data[i+1]

print(transitions[0])

output_file = "./transitions-" + file_path[13:21] + ".csv"

df = pd.DataFrame({'Time' : time, 'motor.m1' : m1_data, 'motor.m2' : m2_data, 'motor.m3' : m3_data, 'motor.m4' : m4_data, 
                   'Pos x': posx_data, 'Pos y': posy_data, 'Pos z': posz_data, 
                   'Vel x': v_x, 'Vel y': v_y, 'Vel z': v_z, 
                   'Quat w': quatw_data, 'Quat x': quatx_data, 'Quat y': quaty_data, 'Quat z': quatz_data})
# df.to_csv(output_file, index=False)