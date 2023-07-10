import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
import sys
import os

"""
This file calculates states, actions and rewards from lab data.
Right now only going through one flight.

First syncs data between drone and mocap, then combines them into states and actions, which are
normalised and saved to csv files. Then calculates rewards based on a goal position and orientation,
and saves to csv file.
"""



# TODO: Change these to be command line arguments, maybe merge all flight data into one file
# Get flight input and mocap data
folder_path_drone = '20230706T15-56-55/'
file_path_battery = './' + folder_path_drone + 'Battery-20230706T15-57-04-timestamped.csv'
file_path_motors = './' + folder_path_drone + 'Motors_fast-20230706T15-57-04-timestamped.csv'
file_path_stab = './' + folder_path_drone + 'Stab-20230706T15-57-03-timestamped.csv'

folder_path_mocap = './mocap_data/'
file_path_mocap = folder_path_mocap + 'Thu_Jul__6_15:57:09_2023/data.csv'

battery_data = pd.read_csv(file_path_battery)
motors_data = pd.read_csv(file_path_motors)
stab_data = pd.read_csv(file_path_stab)

mocap_data = pd.read_csv(file_path_mocap)

# Use mocap data as base for syncing since it has highest data rate
# Sync data sets by linear interpolation
# TODO: check if pitch should be negative
action_pitch    = np.interp(mocap_data['Timestamp'], stab_data['Timestamp'], stab_data['stabilizer.pitch'])
action_roll     = np.interp(mocap_data['Timestamp'], stab_data['Timestamp'], stab_data['stabilizer.roll'])
action_yaw      = np.interp(mocap_data['Timestamp'], stab_data['Timestamp'], stab_data['stabilizer.yaw'])
action_thrust   = np.interp(mocap_data['Timestamp'], stab_data['Timestamp'], stab_data['stabilizer.thrust'])
state_battery   = np.interp(mocap_data['Timestamp'], battery_data['Timestamp'], battery_data['pm.vbat'])
state_motor1    = np.interp(mocap_data['Timestamp'], motors_data['Timestamp'], motors_data['motor.m1'])
state_motor2    = np.interp(mocap_data['Timestamp'], motors_data['Timestamp'], motors_data['motor.m2'])
state_motor3    = np.interp(mocap_data['Timestamp'], motors_data['Timestamp'], motors_data['motor.m3'])
state_motor4    = np.interp(mocap_data['Timestamp'], motors_data['Timestamp'], motors_data['motor.m4'])

# Get rest of state data from mocap
state_posx  = mocap_data['Pos x'].to_numpy()
state_posy  = mocap_data['Pos y'].to_numpy()
state_posz  = mocap_data['Pos z'].to_numpy()
state_quatw = mocap_data['Quat w'].to_numpy()
state_quatx = mocap_data['Quat x'].to_numpy()
state_quaty = mocap_data['Quat y'].to_numpy()
state_quatz = mocap_data['Quat z'].to_numpy()

# Take derivatives to get velocities and angular velocities
state_vx        = np.gradient(state_posx, mocap_data['Timestamp'])
state_vy        = np.gradient(state_posy, mocap_data['Timestamp'])
state_vz        = np.gradient(state_posz, mocap_data['Timestamp'])
state_angvelw   = np.gradient(state_quatw, mocap_data['Timestamp'])
state_angvelx   = np.gradient(state_quatx, mocap_data['Timestamp'])
state_angvely   = np.gradient(state_quaty, mocap_data['Timestamp'])
state_angvelz   = np.gradient(state_quatz, mocap_data['Timestamp'])
action_yawrate  = np.gradient(action_yaw, mocap_data['Timestamp'])

# Plotting interpolated values to sanity check
plotting = False
if plotting:
    plt.subplot(2, 1, 1)
    plt.plot(motors_data['Timestamp'], motors_data['motor.m1'], label='pitch')
    plt.title('')
    plt.ylabel('M1')
    plt.xlabel('Time')

    plt.subplot(2, 1, 2)
    plt.plot(mocap_data['Timestamp'], state_motor1, label='interp pitch')
    plt.ylabel('Interpolated M1')
    plt.xlabel('Time')

    plt.show()



def clip_and_norm_thrust(data):
    # TODO: maybe this is not a good way of doing it for thrusts? Using z-score for now
    data = (1 - (-1)) * (data - 10001) / (60000 - 10001) + (-1)
    data = np.clip(data, -1, 1)

    return data

def clip_and_norm_actions(actions):
    # Clip and normalise actions through Z-score
    for i in range(np.shape(actions)[1]):
        mean = np.mean(actions[:,i])
        std = np.std(actions[:,i])
        actions[:,i] = (actions[:,i] - mean) / std
        actions[:,i] = np.clip(actions[:,i], -1, 1)

    return actions

def normalise_state(state):
    # Normalise states through Z-score
    means = []
    stds = []

    for i in range(np.shape(state)[1]):
        mean = np.mean(state[:,i])
        std = np.std(state[:,i])
        means.append(mean)
        stds.append(std)
        state[:,i] = (state[:,i] - mean) / std

    return state, means, stds

def calculate_rewards(state, goal_position, stable_orientation):
    # Calculate rewards using error between current state and goal state
    # Goal state defined by an arbitrary height, 0 velocity and orientation from when the drone is on the ground
    # --> maximise -sqrt( (curr pos - goal pos)**2 + (curr orientation - stable orientation)**2 )

    # TODO: only include pitch & roll in orientation error?
    # TODO: should different parts of reward be weighted differently?

    pos_error = np.array([state[:,0], state[:,1], state[:,2]]).transpose() - goal_position
    orientation_error = np.array([state[:,3], state[:,4], state[:,5], state[:,6]]).transpose() - stable_orientation

    # Take the norm of each error vector separately to get a vector of rewards https://stackoverflow.com/questions/7741878/how-to-apply-numpy-linalg-norm-to-each-row-of-a-matrix
    rewards = -(np.sum(np.abs(pos_error)**2, axis = -1)**(1./2) + np.sum(np.abs(orientation_error)**2, axis = -1)**(1./2))

    return rewards


def main():

    # Get states, actions and rewards and save to csv for training

    # Actions: commander inputs to CF firmware as (roll, pitch, yawrate, thrust)
    action_data = np.column_stack((action_roll, action_pitch, action_yawrate, action_thrust))
    
    action_data = clip_and_norm_actions(action_data)

    output_file = "./" + "actions.csv"
    action_df = pd.DataFrame({'roll commands': action_data[:,0], 
                              'pitch commands': action_data[:,1], 
                              'yawrate commands': action_data[:,2], 
                              'thrust commands': action_data[:,3]})
    action_df.to_csv(output_file, index=False)


    # State: relative position (y, v_x, v_z), orientation (quaternions w, x, y, z), angular velocities, current motor PWM values, battery voltage
    state_data = np.column_stack((state_posy, state_vx, state_vz, 
                                state_quatw, state_quatx, state_quaty, state_quatz, 
                                state_angvelw, state_angvelx, state_angvely, state_angvelz, 
                                state_motor1, state_motor2, state_motor3, state_motor4, 
                                state_battery))
    
    # Normalise states
    state_data, means, stds = normalise_state(state_data)

    output_file = "./" + "states.csv"
    state_df = pd.DataFrame({'Pos y': state_data[:,0], 'Vel x': state_data[:,1], 'Vel z': state_data[:,2], 
                    'Quat w': state_data[:,3], 'Quat x': state_data[:,4], 'Quat y': state_data[:,5], 'Quat z': state_data[:,6],
                    'Ang vel w': state_data[:,7], 'Ang vel x': state_data[:,8], 'Ang vel y': state_data[:,9], 'Ang vel z': state_data[:,10],
                    'motor.m1' : state_data[:,11], 'motor.m2' : state_data[:,12], 'motor.m3' : state_data[:,13], 'motor.m4' : state_data[:,14],
                    'battery' : state_data[:,15]})
    state_df.to_csv(output_file, index=False)


    # TODO: Check that goal position is reasonable
    # Define goal position and orientation
    goal_alt = 0.4 # [m]
    # Normalise goal altitude, 0 velocity in x and z 
    goal_position = np.array([((goal_alt - means[0]) / stds[0]), 0.0, 0.0]) # [pos_y, vel_x, vel_z]
    
    # Goal orientation when the drone is on a flat surface, average of first 10 samples
    stable_orientation = np.array([np.mean(state_data[:10,7]), np.mean(state_data[:10,8]), np.mean(state_data[:10,9]), np.mean(state_data[:10,10])]) 

    # Calculate rewards for each state
    rewards = calculate_rewards(state_data, goal_position, stable_orientation)

    output_file = "./" + "rewards.csv"
    reward_df = pd.DataFrame({'Rewards': rewards})
    reward_df.to_csv(output_file, index=False)




if __name__=='__main__':
    main()


