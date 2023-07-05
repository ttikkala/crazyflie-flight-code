import signal
import atexit
import time

import pandas as pd
import numpy as np

# for i in range(1000):
#     print(i)
#     time.sleep(1)


# def handle_exit():
#     print('Exiting')


# atexit.register(handle_exit)
# signal.signal(signal.SIGTERM, handle_exit)
# signal.signal(signal.SIGINT, handle_exit)


thrust_file = '~/.config/cfclient/logdata/20230622T11-09-15/Motors-20230622T11-09-19.csv'

data = pd.read_csv(thrust_file)

m1_input = data['motor.m1'].to_numpy()
m2_input = data['motor.m2'].to_numpy()
m3_input = data['motor.m3'].to_numpy()
m4_input = data['motor.m4'].to_numpy()

# stab_thrust_input = data['stabilizer.thrust'].tolist()

motor_inputs = [m1_input, m2_input, m3_input, m4_input]
print(m3_input)
print(motor_inputs[2])