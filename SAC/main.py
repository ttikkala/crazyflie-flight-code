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
import matplotlib.pyplot as plt

device = 'cuda'  # 'cuda' or 'cpu'


# Import data
# TODO: Change this to be a command line argument
folder_path = './Mon-Jul--3-16:55:20-2023/'
# file_path = str(sys.argv[1])
state_path = folder_path + 'states.csv'
rewards_path = folder_path + 'rewards.csv'
actions_path = folder_path + 'actions.csv'

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


# # store data
# folder = 'training_runs'
# file_path = './' + folder + '/' + time.ctime().replace(' ', '_')
# # Create experiment folder
# if not os.path.exists(file_path):
#     os.makedirs(file_path)




# Populate replay buffer with collected flight data
for i in range(np.shape(states)[0] - 1):
    replay.add_sample(observation=states[i], 
                      action=actions[i], 
                      reward=rewards[i], 
                      next_observation=states[i+1], 
                      terminal=0, # Not sure what to put here?
                      env_info={})


# def save_logged_data(file_path, rewards_training):
#     """ Saves logged rewards to a csv file.
#     """
#     with open(
#         os.path.join(file_path,
#             'rewards.csv'), 'a') as fd:
#             cwriter = csv.writer(fd)
#             cwriter.writerow(rewards_training)






def main():

    plt.ion()

    x = np.array([0])
    y = np.array([0])

    plt.ion()
    fig = plt.figure()
    ax=fig.add_subplot(111)
    # ax.set_xlim([0,50])
    # ax.set_ylim([0,2500])
    line,  = ax.plot(x,y)
    plt.show()

    print('Training')
    for i in range(1000):
        agent.single_train_step()
        statistics = agent._algorithm.get_diagnostics()
        print(statistics)

        x = np.append(x,i)
        y = np.append(y,statistics['QF1 Loss'])
        line.set_data(x,y)
        plt.pause(0.01)


if __name__ == '__main__':
    main()
