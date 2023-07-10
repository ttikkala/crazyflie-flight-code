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
# import matplotlib
# matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
import drawnow


device = 'cuda'  # 'cuda' or 'cpu'


# Import data
# TODO: Change this to be a command line argument
folder_path = './'
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


# def draw_fig():
#     plt.plot(x,y)

# x = []
# y = []
# plt.ion()  # enable interactivity
# fig = plt.figure()  # make a figure


# plt.ion()
# fig = plt.figure()
# ax=fig.add_subplot(111)
# ax.set_xlim([0,50])
# ax.set_ylim([0,20])
# ax.plot(x,y)
# plt.show()



# # Create experiment folder
# if not os.path.exists(file_path):
#     os.makedirs(file_path)

file_path = 'losses-' + time.ctime().replace(' ', '-') + '.csv'

with open(file_path, 'a') as fd:
    cwriter = csv.writer(fd)
    cwriter.writerow(['Training step', 'QF1 Loss', 'QF2 Loss', 
                      'Policy Loss', 'Q1 Predictions Mean', 'Q1 Predictions Std', 'Q1 Predictions Max', 
                      'Q2 Predictions Min', 'Q Targets Mean', 'Q Targets Std', 'Q Targets Max', 'Q Targets Min', 
                      'Log Pis Mean', 'Log Pis Std', 'Log Pis Max', 'Log Pis Min', 
                      'Policy mu Mean', 'Policy mu Std', 'Policy mu Max', 'Policy mu Min', 
                      'Policy log std Mean', 'Policy log std Std', 'Policy log std Max', 'Policy log std Min']) 


print('Training')
for i in range(1000):
    agent.single_train_step()
    statistics = agent._algorithm.get_diagnostics()
    print(statistics)

    # x.append(i)
    # y.append(statistics['QF1 Loss'])
    # drawnow.drawnow(draw_fig)

    with open(file_path, 'a') as fd:
        cwriter = csv.writer(fd)
        cwriter.writerow([i, statistics['QF1 Loss'], statistics['QF2 Loss'], 
                    statistics['Policy Loss'], statistics['Q1 Predictions Mean'], statistics['Q1 Predictions Std'], statistics['Q1 Predictions Max'], 
                    statistics['Q2 Predictions Min'], statistics['Q Targets Mean'], statistics['Q Targets Std'], statistics['Q Targets Max'], statistics['Q Targets Min'], 
                    statistics['Log Pis Mean'], statistics['Log Pis Std'], statistics['Log Pis Max'], statistics['Log Pis Min'], 
                    statistics['Policy mu Mean'], statistics['Policy mu Std'], statistics['Policy mu Max'], statistics['Policy mu Min'], 
                    statistics['Policy log std Mean'], statistics['Policy log std Std'], statistics['Policy log std Max'], statistics['Policy log std Min']]) # time.time() is time since 'epoch' - Jan 1 1970 00:00:00




