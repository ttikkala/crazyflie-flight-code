import threading
import natnet_client
import send_thrust_setpoints
import logging
import os
import csv
import time


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
            print(data_in)
        finally:
            logging.debug('Released a lock')
            self.lock.release()


def write_to_csv(file_path, drone_data, opti_data):
    with open(os.path.join(file_path,
            'data.csv'), 'a') as fd:
        cwriter = csv.writer(fd)
        cwriter.writerow([time.time()] + drone_data + opti_data) # time.time() is time since 'epoch' - Jan 1 1970 00:00


def write_drone_opti(drone_thread, opti_thread, file_path):
    drone_data = [0, 0, 0, 0]
    opti_data = [0, 0, 0, 0, 0, 0, 0]

    while True:

        drone_reader.lock.acquire()
        try:
            drone_data = drone_reader.value
            print(drone_data)
        finally:
            drone_reader.lock.release()

        opti_reader.lock.acquire()
        try:
            opti_data = opti_reader.value
            print(opti_data)
        finally:
            opti_reader.lock.release()

        write_to_csv(file_path, drone_data, opti_data)
        time.sleep(0.1)


drone_reader = DataReader()
opti_reader = DataReader()

if __name__ == '__main__':


    folder = 'thrust_mocap_data'
    file_extension = str(time.ctime().replace(' ', '_'))
    file_path = './' + folder + '/' + file_extension

    # Create folder
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    with open(os.path.join(file_path,
        'data.csv'), 'a') as fd:
        cwriter = csv.writer(fd)
        cwriter.writerow(['Time', 'motor.m1', 'motor.m2', 'motor.m3', 'motor.m4', 'RB ID', 'Pos x', 'Pos y', 'Pos z', 'Quat 1', 'Quat 2', 'Quat 3', 'Quat 4']) 
    
    

    drone_thread = threading.Thread(target=send_thrust_setpoints.main)
    opti_thread = threading.Thread(target=natnet_client.main)
    main_thread = threading.Thread(target=write_drone_opti, args=(drone_thread, opti_thread, file_path))

    drone_thread.start()
    opti_thread.start()
    main_thread.start()



