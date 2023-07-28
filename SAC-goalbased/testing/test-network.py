import torch
import pandas as pd
import numpy as np
import csv

policy = torch.load('../training/jul14-policy.pt')


# Import testing data set
actions = pd.read_csv('./actions-testing.csv')
states = pd.read_csv('./states-testing.csv')
rewards = pd.read_csv('./rewards-testing.csv')

actions = actions.to_numpy()
states = states.to_numpy()
rewards = rewards.to_numpy()


rel_errors = []
abs_errors = []

for i in range(np.shape(states)[0]):
    predicted_action = policy(torch.tensor(states[i], dtype=torch.float32, device='cuda'))[0]
    # print(predicted_action.cpu().detach().numpy())
    abs_error = np.abs(predicted_action.cpu().detach().numpy() - actions[i])
    rel_error = np.abs(abs_error / actions[i]) * 100

    if i % 1000 == 0:
        print(i, 'Expected action: ', actions[i])
        print(i, 'Predicted action: ', predicted_action.cpu().detach().numpy())
        # print('Pitch percentage error:', perc_error[1])
    
    abs_errors.append(abs_error)
    rel_errors.append(rel_error)

with open('rel_errors.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(rel_errors)

with open('abs_errors.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(abs_errors)


rel_errors = np.array(rel_errors)
abs_errors = np.array(abs_errors)

print('Mean roll error percentage: %1.2f' %    np.mean(rel_errors[:,0]))
print('Mean pitch error percentage: %1.2f' %   np.mean(rel_errors[:,1]))
print('Mean yawrate error percentage: %1.2f' % np.mean(rel_errors[:,2]))
print('Mean thrust error percentage: %1.2f' %  np.mean(rel_errors[:,3]))

print('Mean roll error absolute: %1.2f' %    np.mean(abs_errors[:,0]))
print('Mean pitch error absolute: %1.2f' %   np.mean(abs_errors[:,1]))
print('Mean yawrate error absolute: %1.2f' % np.mean(abs_errors[:,2]))
print('Mean thrust error absolute: %1.2f' %  np.mean(abs_errors[:,3]))




