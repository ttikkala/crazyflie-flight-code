import replay
import os
import time
import numpy as np
import pandas as pd
import soft_actor_critic
import csv
import torch
import replay
import time

device = 'cuda'  # 'cuda' or 'cpu'


# Import data
file_path = '12:58:51'
# file_path = str(sys.argv[1])
state_path = 'states-' + file_path + '.csv'
rewards_path = 'rewards-' + file_path + '.csv'
actions_path = 'actions-' + file_path + '.csv'

state_data = pd.read_csv(state_path)
rewards_data = pd.read_csv(rewards_path)
actions_data = pd.read_csv(actions_path)

states = state_data.to_numpy()
rewards = rewards_data.to_numpy()
actions = actions_data.to_numpy()

observation_dim = np.shape(states)[1]
action_dim = np.shape(actions)[1]

# initialise replay buffer
replay = replay.SimpleReplayBuffer(
            max_replay_buffer_size=1000000,
            observation_dim=observation_dim,
            action_dim=action_dim,
            env_info_sizes={},)

# initialise networks qf1, qf2, qf1_target, qf2_target, policy
networks = soft_actor_critic.SoftActorCritic._create_networks(obs_dim=observation_dim, action_dim=action_dim)

# Initialise SAC algorithm
agent = soft_actor_critic.SoftActorCritic(replay=replay, networks=networks)


# store data
folder = 'training_runs'
file_path = './' + folder + '/' + time.ctime().replace(' ', '_')
# Create experiment folder
if not os.path.exists(file_path):
    os.makedirs(file_path)




# Populate replay buffer with collected flight data
for i in range(np.shape(states)[0]):
    replay.add_sample(observation=states[i], 
                      action=actions[i], 
                      reward=rewards[i], 
                      next_observation=states[i+1], 
                      terminal=0, # Not sure what to put here?
                      env_info={})



def single_training_step(file_path):
        """
        This function collects first training data, then performs several
        training iterations and finally evaluates the current policy.
        """
        training_iters = 1000
        # Collect training data
        # collect_training_data()
        collect_training_data(True)
        for _ in range(training_iters):
            agent.train(replay)
        # Save the cum. rewards achieved into a csv file
        save_logged_data(file_path, rewards_training=rewards)


def save_logged_data(file_path, rewards_training):
    """ Saves logged rewards to a csv file.
    """
    with open(
        os.path.join(file_path,
            'rewards.csv'), 'a') as fd:
            cwriter = csv.writer(fd)
            cwriter.writerow(rewards_training)




def main():
    for _ in range(5):
        collect_training_data()
    for _ in range(1000):
        single_training_step(file_path)

if __name__ == '__main__':
    main()
