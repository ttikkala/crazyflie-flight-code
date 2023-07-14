import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
import sys
import os

"""
This file adapts the flight data timestamps to real time timestamps.
CF originally records timestamps as ms from starting the client, but we need the real time to sync it with the mocap data.
"""



# TODO: Change these to be command line arguments
# Get flight input and mocap data
folder_path_drone   = '20230706T16-15-00/'
file_path_battery   = './' + folder_path_drone + 'Battery-20230706T16-15-09.csv'
file_path_motors    = './' + folder_path_drone + 'Motors_fast-20230706T16-15-08.csv'
file_path_stab      = './' + folder_path_drone + 'Stab-20230706T16-15-07.csv'

battery_data = pd.read_csv(file_path_battery)
motors_data = pd.read_csv(file_path_motors)
stab_data = pd.read_csv(file_path_stab)


# Get original drone file modification time for syncing (returned as seconds from epoch)
# It turns out that linux doesn't save the creation time of the file for files that are smaller than some threshold,
# so we have to use the modification time instead.
# NB These are also saved in training-data-timestamps.csv for future reference
original_drone_log_path = '/home/tiia/.config/cfclient/logdata/'
stab_log_path = original_drone_log_path + '20230706T16-15-00/Stab-20230706T16-15-07.csv'
battery_log_path = original_drone_log_path + '20230706T16-15-00/Battery-20230706T16-15-09.csv'
motors_log_path = original_drone_log_path + '20230706T16-15-00/Motors_fast-20230706T16-15-08.csv'
# Timestamps of ending recording
stab_timestamp = os.path.getmtime(stab_log_path) # in seconds
battery_timestamp = os.path.getmtime(battery_log_path)
motors_timestamp = os.path.getmtime(motors_log_path)
# Find timestamp of start of recording
stab_timestamp -= (stab_data['Timestamp'][len(stab_data['Timestamp'])-1] - stab_data['Timestamp'][0]) / 1000
battery_timestamp -= (battery_data['Timestamp'][len(battery_data['Timestamp'])-1] - battery_data['Timestamp'][0]) / 1000
motors_timestamp -= (motors_data['Timestamp'][len(motors_data['Timestamp'])-1] - motors_data['Timestamp'][0]) / 1000

# Convert timestamps to seconds from epoch
stab_data['Timestamp'] = (stab_data['Timestamp'] / 1000) - (stab_data['Timestamp'][0] / 1000) + stab_timestamp
battery_data['Timestamp'] = (battery_data['Timestamp'] / 1000) - (battery_data['Timestamp'][0] / 1000) + battery_timestamp
motors_data['Timestamp'] = (motors_data['Timestamp'] / 1000) - (motors_data['Timestamp'][0] / 1000) + motors_timestamp

# New file paths
file_path_stab = file_path_stab[:-4] + '-timestamped.csv'
file_path_battery = file_path_battery[:-4] + '-timestamped.csv'
file_path_motors = file_path_motors[:-4] + '-timestamped.csv'

# Save to file, can take a couple minutes
stab_data.to_csv(file_path_stab, index=False)
battery_data.to_csv(file_path_battery, index=False)
motors_data.to_csv(file_path_motors, index=False)
