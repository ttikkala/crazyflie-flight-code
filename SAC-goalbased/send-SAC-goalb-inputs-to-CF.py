import time
import pandas as pd
import numpy as np
import csv
import os
import torch
import natnet
import attr
import argparse

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
import logging

import threading


###
# This file contains the code for sending the SAC inputs to the Crazyflie
#
# The rough outline of the code is as follows:
# Initialise threads; one for drone data and control, one for OptiTrack data, one for policy network
# Get state in real-time from OptiTrack and drone
# Transform state to normalised state and clip
# Get action from policy
# Transform action to drone command
# Send command to drone
# TODO: Update policy based on reward after each flight
###

# File path for saving actions
file_path_alist = './SAC-goalbased/policy-flight-data/action_list-' + time.ctime().replace(' ', '-') + '.csv'
with open(file_path_alist, 'a') as fd:
    cwriter = csv.writer(fd)
    cwriter.writerow(['Time', 'Roll', 'Pitch', 'Yawrate', 'Thrust']) 

# File path for saving states
file_path_slist = './SAC-goalbased/policy-flight-data/state_list-' + time.ctime().replace(' ', '-') + '.csv'
with open(file_path_slist, 'a') as fd:
    cwriter = csv.writer(fd)
    cwriter.writerow(['Time', 
                     'Pos x', 'Pos y', 'Pos z', 
                     'Vel x', 'Vel z', 
                     'Quat x', 'Quat y', 'Quat z', 'Quat w', 
                     'Ang vel x', 'Ang vel y', 'Ang vel z', 'Ang vel w', 
                     'motor.m1', 'motor.m2', 'motor.m3', 'motor.m4', 
                     'battery', 
                     'goal pos x', 'goal pos y', 'goal pos z', 
                     'goal vel x', 'goal vel z', 
                     'goal quat x', 'goal quat y', 'goal quat z', 'goal quat w'])




# Load policy that was trained using SAC/main.py
policy      = torch.load('./jul31-policy.pt')
# qf1         = torch.load('./SAC/training/jul31-qf1.pt')
# qf2         = torch.load('./SAC/training/jul31-qf2.pt')
# qf1_target  = torch.load('./SAC/training/jul31-qf1_target.pt')
# qf2_target  = torch.load('./SAC/training/jul31-qf2_target.pt')

# Initialise values used for SAC calculations
t_prev = time.time()
x_prev = 0.0
z_prev = 0.0
qx_prev = 0.0
qy_prev = 0.0
qz_prev = 0.0
qw_prev = 0.0

# TODO: Initialise goal position, add a way to calculate this through a function
goal_x = 0.0
goal_y = 0.3
goal_z = 0.0
goal_velx = 0.0
goal_velz = 0.0
# These are already normalised
# goal_qx = 2.5666
# goal_qy = -4.343
# goal_qz = -0.0419
# goal_qw = 0.08032

goal_qx = 0.05149221
goal_qy = 0.65286
goal_qz = 0.016909
goal_qw = 0.480119

# Get means and stds used for SAC normalisation from file
state_means_stds  = pd.read_csv('./SAC-goalbased/jul31-state_means_stds.csv')
action_means_stds = pd.read_csv('./SAC-goalbased/jul31-action_means_stds.csv')

###### CRAZYFLIE DRONE CODE ######
# Crazyflie initialise radio connection
# uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E7E7')

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

drone_signals = [0, 0, 0, 0, 0]

def log_callback(timestamp, data, logconf):
    # print(data)
    global drone_signals
    global drone_reader
    
    drone_signals[0] = data['motor.m1']
    drone_signals[1] = data['motor.m2']
    drone_signals[2] = data['motor.m3']
    drone_signals[3] = data['motor.m4']
    drone_signals[4] = data['pm.vbat']

    # print('Drone signals in: ', [drone_signals[0], drone_signals[1], drone_signals[2], drone_signals[3], drone_signals[4]])

    drone_reader.read_data(drone_signals)


def command_from_network(scf):
    global sac_reader

    time.sleep(4.0)

    while True:
        sac_reader.lock.acquire()
        try:
            action = sac_reader.value
            # print('Drone lock acquired, drone data: ', drone_data)
        finally:
            sac_reader.lock.release()
            time.sleep(0.02) # 50 Hz

        print('Command: ', action[0], action[1], action[2], int(action[3]))
        # TODO: -pitch or pitch?
        # time.sleep(0.1)
        scf.cf.commander.send_notify_setpoint_stop(5)
        scf.cf.commander.send_setpoint(action[0], action[1], action[2], int(action[3])) # roll, pitch, yawrate, thrust



# CF flight code
def fly_drone():

    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    # TODO: Check if this many variables fit in the data stream
    log = LogConfig(name='Data', period_in_ms=10)
    # log.add_variable('stabilizer.thrust', 'float')
    # log.add_variable('stabilizer.roll', 'float')
    # log.add_variable('stabilizer.pitch', 'float')
    # log.add_variable('stabilizer.yaw', 'float')
    log.add_variable('motor.m1', 'float')
    log.add_variable('motor.m2', 'float')
    log.add_variable('motor.m3', 'float')
    log.add_variable('motor.m4', 'float')
    log.add_variable('pm.vbat', 'float')


    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.log.add_config(log)
        log.data_received_cb.add_callback(log_callback)

        log.start()

        scf.cf.commander.send_setpoint(0, 0, 0, 0)

        time.sleep(1.5)

        command_from_network(scf)

        scf.cf.commander.send_setpoint(0, 0, 0, 0)

        log.stop()

        time.sleep(0.1)
        scf.cf.close_link()
    

###### OPTITRACK CODE ######
# Natnet SDK connection to optitrack data stream
@attr.s
class ClientApp(object):

    _client = attr.ib()
    _quiet = attr.ib()

    _last_printed = attr.ib(0)

    @classmethod
    def connect(cls, server_name, rate, quiet):
        if server_name == 'fake':
            client = natnet.fakes.SingleFrameFakeClient.fake_connect(rate=rate)
        else:
            client = natnet.Client.connect(server_name)
        if client is None:
            return None
        return cls(client, quiet)

    def run(self):
        if self._quiet:
            self._client.set_callback(self.callback_quiet)
        else:
            self._client.set_callback(self.callback)
        self._client.spin()

    def callback(self, rigid_bodies, markers, timing):
        """
        :type rigid_bodies: list[RigidBody]
        :type markers: list[LabelledMarker]
        :type timing: TimestampAndLatency
        """
        # print()
        # print('{:.1f}s: Received mocap frame'.format(timing.timestamp))
        global opti_reader

        if rigid_bodies:
            # print('Rigid bodies:')
            for b in rigid_bodies:
            #     print('\t Id {}: ({: 5.2f}, {: 5.2f}, {: 5.2f}), ({: 5.2f}, {: 5.2f}, {: 5.2f}, {: 5.2f})'.format(
            #         b.id_, *(b.position + b.orientation)
            #     ))

                opti_reader.read_data([b.id_, *(b.position + b.orientation)])

    def callback_quiet(self, *_):
        if time.time() - self._last_printed > 1:
            print('.')
            self._last_printed = time.time()


def natnet_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='Will autodiscover if not supplied')
    parser.add_argument('--fake', action='store_true',
                        help='Produce fake data at `rate` instead of connecting to actual server')
    parser.add_argument('--rate', type=float, default=10,
                        help='Rate at which to produce fake data (Hz)')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    try:
        app = ClientApp.connect('fake' if args.fake else args.server, args.rate, args.quiet)
        app.run()
    except natnet.DiscoveryError as e:
        print('Error:', e)

###### THREADING DATA SHARING OBJECT ######
class DataReader(object):

    def __init__(self, start = []):
        self.lock = threading.Lock()
        self.value = start

    def read_data(self, data_in):
        logging.debug('Waiting for a lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            self.value = data_in
            # print('Data in: ', self.value)
        finally:
            logging.debug('Released a lock')
            self.lock.release()
        
        # time.sleep(0.01)

###### SAC CODE ######
def normalise_state(state):
    global state_means_stds

    for i in range(np.shape(state)[0]):
        state[i] = (state[i] - state_means_stds['State means'][i % 18]) / state_means_stds['State stds'][i % 18] 
        state[i] = np.clip(state[i], -1, 1)
        state[i] *= 5
        state[i] = float(state[i])

    return state


def action_to_drone_command(action, noise):
    global action_means_stds

    # Action is input as a torch tensor, detach to get numpy array
    # action = action[0].detach().cpu().numpy()

    # Transform action from normalised value to a real drone command
    # x = (Z * std) + mean
    for i in range(np.shape(action)[0]):
        action[i] = (action[i] * action_means_stds['Action stds'][i]) + action_means_stds['Action means'][i] 

    action[3] *= 1.15

    # Add noise to action
    if noise:
        action += np.random.normal(0, 0.1, 4)

    # Clip thrust to be between 0 and 60000
    action[3] = np.clip(action[3], 0, 60000)

    return action


def get_action(policy, drone_reader, opti_reader):
    global t_prev, x_prev, z_prev, qx_prev, qy_prev, qz_prev, qw_prev

    action_list = []
    state_list = []

    noise = False

    time.sleep(4.0)
    print('#############################################################################################')

    start_time = time.time()
    t_prev = time.time()
    count = 0

    
    while (time.time() - start_time < 6.0):

        # Get state in real-time from OptiTrack and drone
        drone_reader.lock.acquire()
        try:
            drone_data = drone_reader.value
            # print('Drone lock acquired, drone data: ', drone_data)
        finally:
            drone_reader.lock.release()
            time.sleep(0.01)

        opti_reader.lock.acquire()
        try:
            opti_data = opti_reader.value
            # print('Opti lock acquired, opti data: ', opti_data)
        finally:
            opti_reader.lock.release()
            time.sleep(0.01)

        # print('Drone data: ', drone_data)
        # print('Opti data: ', opti_data)

        # Parse data
        # drone_data is in the form [m1, m2, m3, m4, vbat]
        # opti_data is in the form  [id, x,  y,  z,  qx, qy, qz, qw]
        x    = opti_data[1] - 3.698
        y    = opti_data[2]
        z    = opti_data[3] - 2.851
        qx   = opti_data[4]
        qy   = opti_data[5]
        qz   = opti_data[6]
        qw   = opti_data[7]
        m1   = drone_data[0]
        m2   = drone_data[1]
        m3   = drone_data[2]
        m4   = drone_data[3]
        vbat = drone_data[4]


        # Stop drone from crashing from super high all the time and running out of optitrack range
        if y > 0.4 or (x > 1.2 or x < -1.2) or (z > 1.2 or z < -1.2):
            sac_reader.read_data([0, 0, 0, 0])
            print('Not safe!')
            break
        

        # Calculate velocities and angular velocities
        timestep = time.time() - t_prev

        # if count % 10 == 0:
        #     print('timestep: ', timestep)
        #     print('x', x)
        #     print('x prev', x_prev)
        #     print('goal x', goal_x)

        vx       = (x - x_prev) / timestep
        vz       = (z - z_prev) / timestep
        omega_qx = (qx - qx_prev) / timestep
        omega_qy = (qy - qy_prev) / timestep
        omega_qz = (qz - qz_prev) / timestep
        omega_qw = (qw - qw_prev) / timestep

        # Update 'previous' values
        t_prev  = time.time()
        x_prev  = x
        z_prev  = z
        qx_prev = qx
        qy_prev = qy
        qz_prev = qz
        qw_prev = qw


        # Transform state to normalised state and clip
        state = [x, y, z, 
                 vx, vz, 
                 qx, qy, qz, qw, 
                 omega_qx, omega_qy, omega_qz, omega_qw, 
                 m1, m2, m3, m4, 
                 vbat, 
                 goal_x, goal_y, goal_z, 
                 goal_velx, goal_velz, 
                 goal_qx, goal_qy, goal_qz, goal_qw]
        
        # print('before', [x, y, z])
        
        state = normalise_state(state)
        temp = [time.time(), state[0], state[1], state[2], 
                                      state[3], state[4], 
                                      state[5], state[6], state[7], state[8], 
                                      state[9], state[10], state[11], state[12], 
                                      state[13], state[14], state[15], state[16], state[17], 
                                      state[18], state[19], state[20], 
                                      state[21], state[22], 
                                      state[23], state[24], state[25], state[26]]
        state_list.append(temp)

        # print('after', [x, y, z])
        # print('State: ', state[0], state[1], state[2])

        # Get action from policy
        # action = policy(torch.tensor([x, y, z, 
        #                               vx, vz, 
        #                               qx, qy, qz, qw, 
        #                               omega_qx, omega_qy, omega_qz, omega_qw, 
        #                               m1, m2, m3, m4, vbat, 
        #                               goal_x, goal_y, goal_z, 
        #                               goal_velx, goal_velz, 
        #                               goal_qx, goal_qy, goal_qz, goal_qw], device='cuda'))
        action = policy(torch.tensor([state[0], state[1], state[2], 
                                      state[3], state[4], 
                                      state[5], state[6], state[7], state[8], 
                                      state[9], state[10], state[11], state[12], 
                                      state[13], state[14], state[15], state[16], state[17], 
                                      state[18], state[19], state[20], 
                                      state[21], state[22], 
                                      state[23], state[24], state[25], state[26]], device='cuda'))

        # Transform action to drone command
        action = action[0].detach().cpu().numpy()

        if count % 50 == 0:
            noise = True
            action = action_to_drone_command(action, noise)
            noise = False
        else:
            action = action_to_drone_command(action, noise)
        
        temp = [time.time(), action[0], action[1], action[2], action[3]]
        action_list.append(temp)

        sac_reader.read_data(action)

        print('Action: ', action)
        count += 1

        if count % 100 == 0:
            # Save action list to file
            with open(file_path_alist, 'a') as f:
                cwriter = csv.writer(f)
                cwriter.writerows(action_list)
            
            print('Action list saved to file!')
            print('###############################################################################')

            # Save state list to file
            with open(file_path_slist, 'a') as f:
                cwriter = csv.writer(f)
                cwriter.writerows(state_list)

            print('State list saved to file!')
            print('###############################################################################')

            # Reset lists
            action_list = []
            state_list  = []


    sac_reader.read_data([0, 0, 0, 0])
    print('Done!')

    # Save action list to file
    with open(file_path_alist, 'a') as f:
        cwriter = csv.writer(f)
        cwriter.writerows(action_list)
    
    print('Action list saved to file!')
    print('###############################################################################')

    # Save state list to file
    with open(file_path_slist, 'a') as f:
        cwriter = csv.writer(f)
        cwriter.writerows(state_list)

    print('State list saved to file!')
    print('###############################################################################')





# Initialise thread data reader objects
# Used for preventing multiple threads from reading/writing at the same time
drone_reader = DataReader()
opti_reader  = DataReader()
sac_reader   = DataReader()


if __name__ == '__main__':

    # Initialise threads; one for drone data and control, one for OptiTrack data, one for policy network

    drone_thread = threading.Thread(target=fly_drone)
    opti_thread = threading.Thread(target=natnet_main)
    policy_thread = threading.Thread(target=get_action, args=(policy,drone_reader,opti_reader,))

    drone_thread.start()
    opti_thread.start()
    policy_thread.start()


