import rlkit.torch.pytorch_util as ptu
import os
from shutil import copyfile, move
import time
import numpy as np

def move_to_cpu():
    """ Set device to cpu for torch.
    """
    ptu.set_gpu_mode(False)

def move_to_cuda(config):
    """ Set device to CUDA and which GPU, or CPU if not set.

    Args:
        config: Dict containing the configuration.
    """
    if config['use_gpu']:
        if 'cuda_device' in config:
            cuda_device = config['cuda_device']
        else:
            cuda_device = 0
        ptu.set_gpu_mode(True, cuda_device)

def copy_pop_to_ind(networks_pop, networks_ind):
    """ Function used to copy params from pop. networks to individual networks.

    The parameters of all networks in network_ind will be set to the parameters
    of the networks in networks_ind.

    Args:
        networks_pop: Dictonary containing the population networks.
        networks_ind: Dictonary containing the individual networks. These
            networks will be updated.
    """
    for key in networks_pop:
        state_dict = networks_pop[key].state_dict()
        networks_ind[key].load_state_dict(state_dict)
        networks_ind[key].eval()

