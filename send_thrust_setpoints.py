import logging
import time
import csv
import pandas as pd
import os

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

thrust_file = '~/.config/cfclient/logdata/20230616T13-47-02/Motors-20230616T13-48-05.csv'
data = pd.read_csv(thrust_file)

m1_input = data['motor.m1'].tolist()
m2_input = data['motor.m2'].tolist()
m3_input = data['motor.m3'].tolist()
m4_input = data['motor.m4'].tolist()

stab_thrust_input = data['stabilizer.thrust'].tolist()

stab = 0
motor_signals = [0, 0, 0, 0]


# def log_stab_callback(timestamp, data, logconf):
#     print(data)
#     global stab
#     stab = data['stabilizer.thrust']

    # file_path = './' + 'experiment_data' + '/' + file_extension

    # with open(os.path.join(file_path,
    #         'data.csv'), 'a') as fd:
    #     cwriter = csv.writer(fd)
    #     cwriter.writerow([time.time(), stab, 0, 0, 0, 0]) # time.time() is time since 'epoch' - Jan 1 1970 00:00


def log_motor_callback(timestamp, data, logconf):
    print(data)
    global motor_signals
    motor_signals[0] = data['motor.m1']
    motor_signals[1] = data['motor.m2']
    motor_signals[2] = data['motor.m3']
    motor_signals[3] = data['motor.m4']

    global stab
    stab = data['stabilizer.thrust']

    file_path = './' + 'thrust_data' + '/' + file_extension

    with open(os.path.join(file_path,
            'data.csv'), 'a') as fd:
        cwriter = csv.writer(fd)
        cwriter.writerow([time.time(), stab, motor_signals[0], motor_signals[1], motor_signals[2], motor_signals[3]]) # time.time() is time since 'epoch' - Jan 1 1970 00:00




def thrust_ramp(scf):

    thrust_mult = 1
    thrust_step = 500
    thrust = 20000
    pitch = 0
    roll = 0
    yawrate = 0

    # Unlock startup thrust protection
    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    while thrust >= 20000:
        scf.cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
        time.sleep(0.1)
        if thrust >= 25000:
            thrust_mult = -1
        thrust += thrust_step * thrust_mult
    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)
    scf.cf.close_link()


def thrust_from_file(scf):

    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    for thrust in stab_thrust_input:
        time.sleep(0.1)
        scf.cf.commander.send_setpoint(0, 0, 0, thrust) # roll, pitch, yawrate, thrust

    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    time.sleep(0.1)
    scf.cf.close_link()


def ramp_motors(scf):

        thrust_mult = 1
        thrust_step = 500
        time_step = 0.1
        thrust = 0
        pitch = 0
        roll = 0
        yawrate = 0

        # print(scf.cf.calib_a, scf.cf.calib_b)
        # scf.cf._cf.param.set_value('loadcell.a', str(scf.cf.calib_a))
        # scf.cf._cf.param.set_value('loadcell.b', str(scf.cf.calib_b))

        # scf.cf._file = open("data.csv", "w+")
        # scf.cf._file.write("weight[g],pwm,vbat[V],rpm1,rpm2,rpm3,rpm4,v[V],i[A],p[W]\n");

        # The definition of the logconfig can be made before connecting
        scf.cf._lg_stab = LogConfig(name='data', period_in_ms=10)
        scf.cf._lg_stab.add_variable('loadcell.weight', 'float')
        scf.cf._lg_stab.add_variable('pwm.m1_pwm', 'uint16_t')
        scf.cf._lg_stab.add_variable('pm.vbatMV', 'uint16_t')
        scf.cf._lg_stab.add_variable('rpm.m1', 'uint16_t')
        scf.cf._lg_stab.add_variable('rpm.m2', 'uint16_t')
        scf.cf._lg_stab.add_variable('rpm.m3', 'uint16_t')
        scf.cf._lg_stab.add_variable('rpm.m4', 'uint16_t')
        scf.cf._lg_stab.add_variable('asc37800.v_mV', 'int16_t')
        scf.cf._lg_stab.add_variable('asc37800.i_mA', 'int16_t')
        scf.cf._lg_stab.add_variable('asc37800.p_mW', 'int16_t')

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            scf.cf.log.add_config(scf.cf._lg_stab)
            # This callback will receive the data
            scf.cf._lg_stab.data_received_cb.add_callback(scf.cf._stab_log_data)
            # This callback will be called on errors
            scf.cf._lg_stab.error_cb.add_callback(scf.cf._stab_log_error)
            # Start the logging
            scf.cf._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # # Unlock startup thrust protection
        # for i in range(0, 100):
        #     scf.cf._cf.commander.send_setpoint(0, 0, 0, 0)

        # localization = Localization(scf.cf._cf)

        scf.cf.param.set_value('motor.batCompensation', 0)
        scf.cf.param.set_value('motorPowerSet.m1', 0)
        scf.cf.param.set_value('motorPowerSet.enable', 2)
        scf.cf.param.set_value('system.forceArm', 1)

        while scf.cf.is_connected: #thrust >= 0:
            thrust += thrust_step * thrust_mult
            if thrust >= 65536 or thrust < 0:
            # if thrust >= 20000 or thrust < 0:
                thrust_mult *= -1
                thrust += thrust_step * thrust_mult
            print(thrust)
            # scf.cf._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            # localization.send_emergency_stop_watchdog()
            scf.cf._cf.param.set_value('motorPowerSet.m1', str(thrust))
            time.sleep(time_step)

        # scf.cf._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        # time.sleep(0.1)
        # scf.cf._cf.close_link()



if __name__ == '__main__':
    
    file_extension = str(time.ctime().replace(' ', '_'))
    folder = 'thrust_data'
    file_path = './' + folder + '/' + file_extension

    # Create folder
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    with open(os.path.join(file_path,
            'data.csv'), 'a') as fd:
        cwriter = csv.writer(fd)
        cwriter.writerow(['Time', 'stabilizer.thrust', 'motor.m1', 'motor.m2', 'motor.m3', 'motor.m4']) 
    
    
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_motor = LogConfig(name='Data', period_in_ms=10)
    lg_motor.add_variable('stabilizer.thrust', 'float')
    # lg_motor = LogConfig(name='Motors', period_in_ms=10)
    lg_motor.add_variable('motor.m1', 'float')
    lg_motor.add_variable('motor.m2', 'float')
    lg_motor.add_variable('motor.m3', 'float')
    lg_motor.add_variable('motor.m4', 'float')

    

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        # scf.cf.log.add_config(lg_stab)
        # lg_stab.data_received_cb.add_callback(log_stab_callback)
        scf.cf.log.add_config(lg_motor)
        lg_motor.data_received_cb.add_callback(log_motor_callback)


        lg_motor.start()
        # lg_stab.start()

        # thrust_ramp(scf)
        thrust_from_file(scf)

        lg_motor.stop()
        # lg_stab.stop()