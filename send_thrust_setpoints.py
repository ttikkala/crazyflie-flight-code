import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

thrust_file = '~/.config/cfclient/logdata/20230614T11-16-14/Motors-20230614T11-16-23.csv'



def simple_log(scf, logconf):

    with SyncLogger(scf, lg_stab) as logger_stab: 
        with SyncLogger(scf, lg_motor) as logger_motor:

            for log_entry_stab in logger_stab:
                for log_entry_motor in logger_motor:

                    timestamp_stab = log_entry_stab[0]
                    data_stab = log_entry_stab[1]
                    logconf_name_stab = log_entry_stab[2]

                    timestamp_motor = log_entry_motor[0]
                    data_motor = log_entry_motor[1]
                    logconf_name_motor = log_entry_motor[2]

                    print('[%d][%s]: %s' % (timestamp_stab, logconf_name_stab, data_stab))
                    print('[%d][%s]: %s' % (timestamp_motor, logconf_name_motor, data_motor))

                    break


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.thrust', 'float')
    lg_motor = LogConfig(name='Motors', period_in_ms=10)
    lg_motor.add_variable('motor.m1', 'float')
    lg_motor.add_variable('motor.m2', 'float')
    lg_motor.add_variable('motor.m3', 'float')
    lg_motor.add_variable('motor.m4', 'float')


    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        # simple_connect()

        simple_log(scf, lg_stab)
        simple_log(scf, lg_motor)