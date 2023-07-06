import time
import pandas as pd
import numpy as np
import csv
import os

# thrust_file = '~/.config/cfclient/logdata/20230704T10-33-05/Stab-20230704T10-34-00.csv'
# thrust_file = '~/.config/cfclient/logdata/20230704T11-09-49/Stab-20230704T11-10-42.csv'
# thrust_file = '~/.config/cfclient/logdata/20230704T11-36-14/Stab-20230704T11-38-58.csv'
# thrust_file = '~/.config/cfclient/logdata/20230705T13-30-14/Stab-20230705T13-31-35.csv'
# thrust_file = '~/.config/cfclient/logdata/20230705T14-09-08/Stab-20230705T14-11-53.csv' # Should move forward just a little bit
# thrust_file = '~/.config/cfclient/logdata/20230705T14-36-06/Stab-20230705T14-37-10.csv'
# thrust_file = '~/.config/cfclient/logdata/20230705T15-01-05/Stab-20230705T15-02-08.csv'

# thrust_file = '~/.config/cfclient/logdata/20230705T16-09-00/Stab-20230705T16-09-07.csv' # front & back
# thrust_file = '~/.config/cfclient/logdata/20230705T16-24-01/Stab-20230705T16-24-09.csv' # flies around a bit, hovers for a while, goes slightly to the back left

thrust_file = '~/.config/cfclient/logdata/20230706T09-23-40/Stab-20230706T09-24-15.csv'

data = pd.read_csv(thrust_file)

# m1_input = data['motor.m1'].tolist()
# m2_input = data['motor.m2'].tolist()
# m3_input = data['motor.m3'].tolist()
# m4_input = data['motor.m4'].tolist()

stab_thrust_input = data['stabilizer.thrust'].tolist()
stab_roll_input = data['stabilizer.roll'].tolist()
stab_pitch_input = data['stabilizer.pitch'].tolist()
stab_yaw_input = data['stabilizer.yaw'].tolist()



def thrust_ramp(scf):

    thrust_mult = 1
    thrust_step = 500
    thrust = 10001
    pitch = 0
    roll = 0
    yawrate = 0

    # Unlock startup thrust protection
    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    while thrust >= 10001:
        scf.cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
        time.sleep(0.1)
        if thrust >= 11000:
            thrust_mult = -1
        thrust += thrust_step * thrust_mult
    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)
    scf.cf.close_link()


def thrust_from_file(scf):
    global thrust_file

    data = pd.read_csv(thrust_file)

    # m1_input = data['motor.m1'].tolist()
    # m2_input = data['motor.m2'].tolist()
    # m3_input = data['motor.m3'].tolist()
    # m4_input = data['motor.m4'].tolist()

    time_flight = data['Timestamp'] / 1000
    time_flight = time_flight - time_flight[0]
    time_flight = time_flight.to_numpy()

    stab_thrust_input   = data['stabilizer.thrust'].to_numpy(copy=True)
    stab_roll_input     = data['stabilizer.roll'].to_numpy(copy=True)
    stab_pitch_input    = data['stabilizer.pitch'].to_numpy(copy=True)
    stab_yaw_input      = data['stabilizer.yaw'].to_numpy(copy=True)
    stab_yawrate_input  = np.gradient(stab_yaw_input, time_flight)

    # Unlock startup thrust protection
    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    bla = []

    with open(os.path.join('./flight_inputs',
        'inputs.csv'), 'a') as fd:

        for i in range(len(stab_thrust_input)):
            time.sleep(0.01)
            # Send previous flight control data to cf, note that pitch is recorded in the UI as -pitch for some godforsaken reason
            scf.cf.commander.send_notify_setpoint_stop()
            scf.cf.commander.send_setpoint(stab_roll_input[i], -stab_pitch_input[i], stab_yawrate_input[i], int(stab_thrust_input[i])) # roll, pitch, yawrate, thrust
            bla.append([time.time(), stab_roll_input[i], -stab_pitch_input[i], stab_yawrate_input[i], int(stab_thrust_input[i])])


            if len(bla) > 100:
                cwriter = csv.writer(fd)
                cwriter.writerows(bla)
                bla = []
            # cwriter = csv.writer(fd)
            # cwriter.writerow([time.time(), stab_roll_input[i], -stab_pitch_input[i], stab_yawrate_input[i], int(stab_thrust_input[i])])

    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    time.sleep(0.1)
    scf.cf.close_link()



def ramp_motors(scf):

        thrust_mult = 1
        thrust_step = 500
        time_step = 0.1
        thrust = 5000
        pitch = 0
        roll = 0
        yawrate = 0

        scf.cf.commander.send_setpoint(0, 0, 0, 0)

        # scf.cf.param.set_value('motor.batCompensation', 0)
        # scf.cf.param._initialized.set()
        scf.cf.param.set_value('motorPowerSet.m1', 5)
        scf.cf.param.set_value('motorPowerSet.m2', 0)
        scf.cf.param.set_value('motorPowerSet.m3', 0)
        scf.cf.param.set_value('motorPowerSet.m4', 0)
        scf.cf.param.set_value('motorPowerSet.enable', 2)
        scf.cf.param.set_value('system.forceArm', 1)

        while scf.cf.is_connected: #thrust >= 0:
            thrust += thrust_step * thrust_mult
            if thrust >= 13000 or thrust < 0:
                thrust_mult *= -1
                thrust += thrust_step * thrust_mult
            print(thrust)

            scf.cf.param.set_value('motorPowerSet.m1', str(thrust))
            scf.cf.param.set_value('motorPowerSet.m2', str(thrust))
            scf.cf.param.set_value('motorPowerSet.m3', str(thrust))
            scf.cf.param.set_value('motorPowerSet.m4', str(thrust))
            time.sleep(time_step)


        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        scf.cf.close_link()


def motors_from_file(scf):

    data = pd.read_csv(thrust_file)

    m1_input = data['motor.m1'].to_numpy()
    m2_input = data['motor.m2'].to_numpy()
    m3_input = data['motor.m3'].to_numpy()
    m4_input = data['motor.m4'].to_numpy()

    # stab_thrust_input = data['stabilizer.thrust'].tolist()

    motor_inputs = [m1_input, m2_input, m3_input, m4_input]
     
    scf.cf.param.set_value('motorPowerSet.m1', 0)
    scf.cf.param.set_value('motorPowerSet.m2', 0)
    scf.cf.param.set_value('motorPowerSet.m3', 0)
    scf.cf.param.set_value('motorPowerSet.m4', 0)
    scf.cf.param.set_value('motorPowerSet.enable', 2)
    scf.cf.param.set_value('system.forceArm', 1)

    while scf.cf.is_connected:
        for idx in range(len(motor_inputs[0])):
            time.sleep(0.05)
            scf.cf.param.set_value('motorPowerSet.m1', str(motor_inputs[0][idx]))
            scf.cf.param.set_value('motorPowerSet.m2', str(motor_inputs[1][idx]))
            scf.cf.param.set_value('motorPowerSet.m3', str(motor_inputs[2][idx]))
            scf.cf.param.set_value('motorPowerSet.m4', str(motor_inputs[3][idx]))
            print('Motor inputs: ', [motor_inputs[0][idx], motor_inputs[1][idx], motor_inputs[2][idx], motor_inputs[3][idx]])


def hover_auto(scf):

    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    scf.cf.commander.send_hover_setpoint(0, 0, 0, 0.1)
    time.sleep(1)
    scf.cf.commander.send_hover_setpoint(0, 0, 0, 0)


