import time
import pandas as pd
import numpy as np

thrust_file = '~/.config/cfclient/logdata/20230703T16-48-50/Stab-20230703T16-52-12.csv'
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

    # time_flight = data['time'].tolist() / 1000

    stab_thrust_input   = data['stabilizer.thrust'].tolist()
    stab_roll_input     = data['stabilizer.roll'].tolist()
    stab_pitch_input    = data['stabilizer.pitch'].tolist()
    stab_yaw_input      = data['stabilizer.yaw'].tolist()
    # stab_yawrate_input  = np.gradient(stab_yaw_input, time_flight)

    scf.cf.commander.send_setpoint(0, 0, 0, 0)

    for i in range(len(stab_thrust_input)):
        time.sleep(0.01)
        # Send previous flight control data to cf, note that pitch is recorded in the UI as -pitch for some godforsaken reason
        scf.cf.commander.send_setpoint(stab_roll_input[i], -stab_pitch_input[i], 0, int(stab_thrust_input[i])) # roll, pitch, yawrate, thrust

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


