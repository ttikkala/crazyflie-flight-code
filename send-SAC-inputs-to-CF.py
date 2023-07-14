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

# Load policy
policy = torch.load('policy.pt')

# Initialise threads; one for drone data and control, one for OptiTrack data, one for policy network


# Get state in real-time from OptiTrack and drone


# Transform state to normalised state and clip


# Get action from policy


# Transform action to drone command


# Send command to drone


# Update policy based on reward?






# Crazyflie initialise radio connection
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
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

    print('Drone signals in: ', [drone_signals[0], drone_signals[1], drone_signals[2], drone_signals[3], drone_signals[4]])

    drone_reader.read_data(drone_signals)


def command_from_network(scf, roll, pitch, yawrate, thrust):

    # time.sleep(0.1)
    scf.cf.commander.send_setpoint(roll, pitch, yawrate, thrust) # roll, pitch, yawrate, thrust



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

        command_from_network(scf)

        scf.cf.commander.send_setpoint(0, 0, 0, 0)

        log.stop()

        time.sleep(0.1)
        scf.cf.close_link()
    

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
            print('Data in: ', self.value)
        finally:
            logging.debug('Released a lock')
            self.lock.release()
        
        # time.sleep(0.01)


def get_action(policy, drone_reader, opti_reader):

    while True:
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


        # drone_data is in the form [m1, m2, m3, m4, vbat]
        # opti_data is in the form [id, x, y, z, qx, qy, qz, qw]
        y    = opti_data[2]
        qx   = opti_data[4]
        qy   = opti_data[5]
        qz   = opti_data[6]
        qw   = opti_data[7]
        m1   = drone_data[0]
        m2   = drone_data[1]
        m3   = drone_data[2]
        m4   = drone_data[3]
        vbat = drone_data[4]
        

        # TODO: need timestep somehow and previous state
        timestep = 0.01  
        vx       = abs(opti_data[1] - x_prev) / timestep
        vz       = abs(opti_data[3] - z_prev) / timestep
        omega_qx = abs(qx - qx_prev) / timestep
        omega_qy = abs(qy - qy_prev) / timestep
        omega_qz = abs(qz - qz_prev) / timestep
        omega_qw = abs(qw - qw_prev) / timestep


        # Transform state to normalised state and clip
        state = [y, vx, vz, qx, qy, qz, qw, omega_qx, omega_qy, omega_qz, omega_qw, m1, m2, m3, m4, vbat]
        state = normalise_state(state)

        # Get action from policy
        action = policy(torch.tensor([y, vx, vz, qx, qy, qz, qw, omega_qx, omega_qy, omega_qz, omega_qw, m1, m2, m3, m4, vbat]))

        # Transform action to drone command
        action = action_to_drone_command(action)


# TODO: how to send action to drone?


drone_reader = DataReader()
opti_reader = DataReader()


if __name__ == '__main__':

    # Initialise threads; one for drone data and control, one for OptiTrack data, one for policy network

    drone_thread = threading.Thread(target=fly_drone)
    opti_thread = threading.Thread(target=natnet_main)
    policy_thread = threading.Thread(target=get_action, args=(policy,drone_reader,opti_reader,))

    drone_thread.start()
    opti_thread.start()
    policy_thread.start()


