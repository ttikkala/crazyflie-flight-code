import torch
import time

# Check if cuda is available
print(torch.cuda.is_available())

pol = torch.load('policy.pt')
print(pol(torch.tensor([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], dtype=torch.float32).to('cuda')))

