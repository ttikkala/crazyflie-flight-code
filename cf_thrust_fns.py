import time
import pandas as pd
import numpy as np

thrust_file = '~/.config/cfclient/logdata/20230626T11-17-16/Motors-20230626T11-17-20.csv'
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


def thrust_from_file(scf):
    global thrust_file

    data = pd.read_csv(thrust_file)

    # m1_input = data['motor.m1'].tolist()
    # m2_input = data['motor.m2'].tolist()
    # m3_input = data['motor.m3'].tolist()
    # m4_input = data['motor.m4'].tolist()

    stab_thrust_input = data['stabilizer.thrust'].tolist()

    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    for thrust in stab_thrust_input:
        time.sleep(0.1)
        scf.cf.commander.send_setpoint(-1.2, -1.8, 0, thrust) # roll, pitch, yawrate, thrust

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


