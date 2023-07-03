import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
import sys

folder_path = './Mon-Jun-26-12:58:51-2023/'
file_path = './Mon-Jun-26-12:58:51-2023/data.csv'
# file_path = str(sys.argv[1])


flight_data = pd.read_csv(file_path)

time = np.array(flight_data['Time'].tolist())

m1_data = np.array(flight_data['motor.m1'].tolist())
m2_data = np.array(flight_data['motor.m2'].tolist())
m3_data = np.array(flight_data['motor.m3'].tolist())
m4_data = np.array(flight_data['motor.m4'].tolist())

# Disgusting fix for a truly stupid problem
motor_data_input_path = '~/.config/cfclient/logdata/20230626T11-17-16/Motors-20230626T11-17-20.csv'
motor_data_input = pd.read_csv(motor_data_input_path)
thrust_data_temp = np.array(motor_data_input['stabilizer.thrust'].tolist())
start_idx = np.argmax(thrust_data_temp > 0)
thrust_data_temp = thrust_data_temp[start_idx:]
thrust_data = []

for i in range(len(thrust_data_temp)):
    for j in range(10):
        thrust_data.append(thrust_data_temp[i])

thrust_data = np.array(thrust_data)

print(thrust_data)

posx_data = np.array(flight_data['Pos x'].tolist())
posy_data = np.array(flight_data['Pos y'].tolist())
posz_data = np.array(flight_data['Pos z'].tolist())
quatw_data = np.array(flight_data['Quat 1'].tolist())
quatx_data = np.array(flight_data['Quat 2'].tolist())
quaty_data = np.array(flight_data['Quat 3'].tolist())
quatz_data = np.array(flight_data['Quat 4'].tolist())

start_time_idx = np.argmax(m1_data > 0)

# Get time and remove data entries before recording starts (there's some unusable lines of all zeroes first)
time = time - time[start_time_idx]
time = time[start_time_idx:]

# Motor data
m1_data = m1_data[start_time_idx:]
m2_data = m2_data[start_time_idx:]
m3_data = m3_data[start_time_idx:]
m4_data = m4_data[start_time_idx:]

thrust_data = thrust_data[:len(m1_data)]

# Get position and orientation data
posx_data = posx_data[start_time_idx:]
posy_data = posy_data[start_time_idx:]
posz_data = posz_data[start_time_idx:]
quatw_data = quatw_data[start_time_idx:]
quatx_data = quatx_data[start_time_idx:]
quaty_data = quaty_data[start_time_idx:]
quatz_data = quatz_data[start_time_idx:]

# Take derivatives to get velocities and angular velocities
v_x = np.gradient(posx_data, time)
v_y = np.gradient(posy_data, time)
v_z = np.gradient(posz_data, time)
ang_vel_w = np.gradient(quatw_data, time)
ang_vel_x = np.gradient(quatx_data, time)
ang_vel_y = np.gradient(quaty_data, time)
ang_vel_z = np.gradient(quatz_data, time)

# Sanity check derivatives by plotting
plotting = False
if plotting:
    plt.subplot(2, 1, 1)
    plt.plot(time, posx_data, 'ko-')
    plt.title('')
    plt.ylabel('Position in x')
    plt.xlabel('Time')

    plt.subplot(2, 1, 2)
    plt.plot(time, v_x, 'r.-')
    plt.ylabel('Velocity in x')
    plt.xlabel('Time')

    plt.show()



# output_file = "./data-clean-" + file_path[13:21] + ".csv"
# df = pd.DataFrame({'Time' : time, 'motor.m1' : m1_data, 'motor.m2' : m2_data, 'motor.m3' : m3_data, 'motor.m4' : m4_data, 
#                    'Pos x': posx_data, 'Pos y': posy_data, 'Pos z': posz_data, 
#                    'Vel x': v_x, 'Vel y': v_y, 'Vel z': v_z, 
#                    'Quat w': quatw_data, 'Quat x': quatx_data, 'Quat y': quaty_data, 'Quat z': quatz_data})
# df.to_csv(output_file, index=False)



def clip_and_norm_actions(data):
    data = (1 - (-1)) * (data - 10001) / (60000 - 10001) + (-1)
    data = np.clip(data, -1, 1)

    return data

def normalise_state(state):
    # Normalise states through Z-score
    for i in range(np.shape(state)[1]):
        mean = np.mean(state[:,i])
        std = np.std(state[:,i])
        state[:,i] = (state[:,i] - mean) / std

    return state

def calculate_rewards(state, goal_position, stable_orientation):
    # Calculate rewards
    # maximise -sqrt( (curr pos - goal pos)**2 + (curr orientation - stable orientation)**2 )

    pos_error = np.array([state[:,0], state[:,1], state[:,2]]).transpose() - goal_position
    orientation_error = np.array([state[:,3], state[:,4], state[:,5], state[:,6]]).transpose() - stable_orientation

    # Take the norm of each error vector separately to get a vector of rewards https://stackoverflow.com/questions/7741878/how-to-apply-numpy-linalg-norm-to-each-row-of-a-matrix
    rewards = -(np.sum(np.abs(pos_error)**2, axis = -1)**(1./2) + np.sum(np.abs(orientation_error)**2, axis = -1)**(1./2))

    return rewards


def main():

    # Normalise and clip motor values to get actions
    # m1_actions = clip_and_norm_actions(m1_data)
    # m2_actions = clip_and_norm_actions(m2_data)
    # m3_actions = clip_and_norm_actions(m3_data)
    # m4_actions = clip_and_norm_actions(m4_data)

    # Actions: thrust inputs to drone motors
    # action_data = np.column_stack((m1_actions[1:], m2_actions[1:], m3_actions[1:], m4_actions[1:]))
    action_data = clip_and_norm_actions(thrust_data)

    output_file = folder_path + "actions.csv"
    action_df = pd.DataFrame({'thrust commands': action_data})
    action_df.to_csv(output_file, index=False)



    # State: relative position (y, v_x, v_z), orientation, angular velocities, current motor PWM values
    state_data = np.column_stack((posy_data, v_x, v_z, 
                                quatw_data, quatx_data, quaty_data, quatz_data, 
                                ang_vel_w, ang_vel_x, ang_vel_y, ang_vel_z, 
                                m1_data, m2_data, m3_data, m4_data))
    
    # Normalise state
    state_data = normalise_state(state_data)

    output_file = folder_path + "states.csv"
    state_df = pd.DataFrame({'Pos y': state_data[:,0], 'Vel x': state_data[:,1], 'Vel z': state_data[:,2], 
                    'Quat w': state_data[:,3], 'Quat x': state_data[:,4], 'Quat y': state_data[:,5], 'Quat z': state_data[:,6],
                    'Ang vel w': state_data[:,7], 'Ang vel x': state_data[:,8], 'Ang vel y': state_data[:,9], 'Ang vel z': state_data[:,10],
                    'motor.m1' : state_data[:,11], 'motor.m2' : state_data[:,12], 'motor.m3' : state_data[:,13], 'motor.m4' : state_data[:,14]})
    state_df.to_csv(output_file, index=False)




    # TODO: Pick goal position and check orientation in lab
    # Define goal position and orientation
    goal_position = np.array([0.1, 0.0, 0.0]) # [pos_y, vel_x, vel_z]
    stable_orientation = np.array([0.0, 0.0, 0.0, 0.0]) # orientation when the drone is on a flat surface

    # Calc rewards for each state
    rewards = calculate_rewards(state_data, goal_position, stable_orientation)
    print(np.shape(rewards))

    output_file = folder_path + "rewards.csv"
    reward_df = pd.DataFrame({'Rewards': rewards})
    reward_df.to_csv(output_file, index=False)




if __name__=='__main__':
    main()








######################### TRASH #########################

# transitions = np.zeros(((np.shape(posx_data)[0] - 1), 24))
# print(transitions)

# print(state_data[0])
# print(action_data[0])
# print(state_data[1])


# for i in range(np.shape(posx_data)[0] - 1):
#     transitions[i][:10] = state_data[i]
#     transitions[i][10:14] = action_data[i]
#     transitions[i][14:] = state_data[i+1]

# print(transitions[0])

# output_file = "./transitions-" + file_path[13:21] + ".csv"

# np.savetxt("transitions.csv", transitions, delimiter=',')


# df = pd.DataFrame({'Pos x': transitions[:,0], 'Pos y': transitions[:,1], 'Pos z': transitions[:,2], 
#                    'Vel x': transitions[:,3], 'Vel y': transitions[:,4], 'Vel z': transitions[:,5], 
#                    'Quat w': transitions[:,6], 'Quat x': transitions[:,7], 'Quat y': transitions[:,8], 'Quat z': transitions[:,9],
#                    'motor.m1' : transitions[:,10], 'motor.m2' : transitions[:,11], 'motor.m3' : transitions[:,12], 'motor.m4' : transitions[:,13], 
#                    'Next Pos x': transitions[:,14], 'Next Pos y': transitions[:,15], 'Next Pos z': transitions[:,16], 
#                    'Next Vel x': transitions[:,17], 'Next Vel y': transitions[:,18], 'Next Vel z': transitions[:,19], 
#                    'Next Quat w': transitions[:,20], 'Next Quat x': transitions[:,21], 'Next Quat y': transitions[:,22], 'Next Quat z': transitions[:,23]})
# df.to_csv(output_file, index=False)

