import torch
import pandas as pd
import numpy as np
import replay
import soft_actor_critic

qf1         = torch.load('jul31-qf1.pt')
qf2         = torch.load('jul31-qf2.pt')
qf1_target  = torch.load('jul31-qf1_target.pt')
qf2_target  = torch.load('jul31-qf2_target.pt')
policy      = torch.load('jul31-policy.pt')

networks = {'qf1' : qf1, 'qf2' : qf2, 'qf1_target' : qf1_target, 'qf2_target' : qf2_target, 'policy' : policy}

# Flight data to replay buffer
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

for i in range(np.shape(states)[0] - 1):
    replay.add_sample(observation=states[i], 
                      action=actions[i], 
                      reward=rewards[i], 
                      next_observation=states[i+1], 
                      terminal=0, 
                      env_info={})



agent = soft_actor_critic.SoftActorCritic(replay=replay, networks=networks)

agent.single_train_step()

# Save policy and Q-function networks torch objects for future use
# TODO: naming
torch.save(agent._algorithm.policy,     'flight1-policy.pt')
torch.save(agent._algorithm.qf1,        'flight1-qf1.pt')
torch.save(agent._algorithm.qf2,        'flight1-qf2.pt')
torch.save(agent._algorithm.target_qf1, 'flight1-qf1_target.pt')
torch.save(agent._algorithm.target_qf2, 'flight1-qf2_target.pt')



