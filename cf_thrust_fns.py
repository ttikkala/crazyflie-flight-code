import time
import pandas as pd


thrust_file = '~/.config/cfclient/logdata/20230621T09-53-19/Motors-20230621T09-54-06.csv'
data = pd.read_csv(thrust_file)

m1_input = data['motor.m1'].tolist()
m2_input = data['motor.m2'].tolist()
m3_input = data['motor.m3'].tolist()
m4_input = data['motor.m4'].tolist()

stab_thrust_input = data['stabilizer.thrust'].tolist()


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


def thrust_from_file(scf, thrust_file):

    data = pd.read_csv(thrust_file)

    # m1_input = data['motor.m1'].tolist()
    # m2_input = data['motor.m2'].tolist()
    # m3_input = data['motor.m3'].tolist()
    # m4_input = data['motor.m4'].tolist()

    stab_thrust_input = data['stabilizer.thrust'].tolist()

    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    for thrust in stab_thrust_input:
        time.sleep(0.1)
        scf.cf.commander.send_setpoint(0, 0, 0, thrust) # roll, pitch, yawrate, thrust

    scf.cf.commander.send_setpoint(0, 0, 0, 0)
    time.sleep(0.1)
    scf.cf.close_link()
