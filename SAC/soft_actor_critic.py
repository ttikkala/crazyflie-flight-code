#########

# From co-adaptation code, using rlkit version 0.2.1

#########


from rlkit.torch.sac.policies import TanhGaussianPolicy
# from rlkit.torch.sac.sac import SoftActorCritic
from rlkit.torch.networks import FlattenMlp
import numpy as np
from rl_algorithm import RL_algorithm
from rlkit.torch.sac.sac import SACTrainer
import rlkit.torch.pytorch_util as ptu
import torch
import utils
import matplotlib.pyplot as plt
import matplotlib

class SoftActorCritic(RL_algorithm):

    def __init__(self, 
                #  config, 
                #  env, 
                 replay, 
                 networks):
        """ Basically a wrapper class for SAC from rlkit.

        Args:
            replay: Replay buffer
            networks: dict containing the networks.

        """
        super().__init__(replay, 
                         networks
                        # config, 
                        #  env, 
                        )

        self._qf1 = networks['qf1']
        self._qf2 = networks['qf2']
        self._qf1_target = networks['qf1_target']
        self._qf2_target = networks['qf2_target']
        self._policy = networks['policy']

        self._batch_size = 64
        self._nmbr_updates = 1000

        self._algorithm = SACTrainer(
            # env=self._env,
            policy=self._policy,
            qf1=self._qf1,
            qf2=self._qf2,
            target_qf1=self._qf1_target,
            target_qf2=self._qf2_target,
            use_automatic_entropy_tuning = False,
            alpha=0.01,
        )

        # self._algorithm_ind.to(ptu.device)
        # self._algorithm_pop.to(ptu.device)

    def episode_init(self):
        """ Initializations to be done before the first episode.

        In this case basically creates a fresh instance of SAC for the
        individual networks and copies the values of the target network.
        """
        self._algorithm = SACTrainer(
            # env=self._env,
            policy=self._policy,
            qf1=self._qf1,
            qf2=self._qf2,
            target_qf1=self._qf1_target,
            target_qf2=self._qf2_target,
            use_automatic_entropy_tuning = False,
            # alt_alpha = self._alt_alpha,
        )
        # if self._config['rl_algorithm_config']['copy_from_gobal']:
        #     utils.copy_pop_to_ind(networks_pop=self._networks['population'], networks_ind=self._networks['individual'])
        # We have only to do this becasue the version of rlkit which we use
        # creates internally a target network
        # vf_dict = self._algorithm_pop.target_vf.state_dict()
        # self._algorithm_ind.target_vf.load_state_dict(vf_dict)
        # self._algorithm_ind.target_vf.eval()
        # self._algorithm_ind.to(ptu.device)

    def single_train_step(self):
        """ 
        A single training step.
        """

        # self._algorithm_ind.num_updates_per_train_call = self._variant_spec['num_updates_per_epoch']
        # self._algorithm_ind._try_to_train()
        for _ in range(self._nmbr_updates):
            batch = self._replay.random_batch(self._batch_size)
            self._algorithm.train(batch)



    # @staticmethod
    # def create_networks(env, config):
    #     """ Creates all networks necessary for SAC.

    #     These networks have to be created before instantiating this class and
    #     used in the constructor.

    #     Args:
    #         config: A configuration dictonary containing population and
    #             individual networks

    #     Returns:
    #         A dictonary which contains the networks.
    #     """
    #     network_dict = {
    #         'individual' : SoftActorCritic._create_networks(env=env, config=config),
    #         'population' : SoftActorCritic._create_networks(env=env, config=config),
    #     }
    #     return network_dict

    @staticmethod
    def _create_networks(obs_dim, action_dim):
        """ Creates all networks necessary for SAC.

        These networks have to be created before instantiating this class and
        used in the constructor.

        TODO: Maybe this should be reworked one day...

        Args:
            config: A configuration dictonary.

        Returns:
            A dictonary which contains the networks.
        """
        obs_dim = obs_dim
        action_dim = action_dim
        net_size = 256
        hidden_sizes = [256] * 3
        # hidden_sizes = [net_size, net_size, net_size]
        qf1 = FlattenMlp(
            hidden_sizes=hidden_sizes,
            input_size=obs_dim + action_dim,
            output_size=1,
        ).to(device=ptu.device)
        qf2 = FlattenMlp(
            hidden_sizes=hidden_sizes,
            input_size=obs_dim + action_dim,
            output_size=1,
        ).to(device=ptu.device)
        qf1_target = FlattenMlp(
            hidden_sizes=hidden_sizes,
            input_size=obs_dim + action_dim,
            output_size=1,
        ).to(device=ptu.device)
        qf2_target = FlattenMlp(
            hidden_sizes=hidden_sizes,
            input_size=obs_dim + action_dim,
            output_size=1,
        ).to(device=ptu.device)
        policy = TanhGaussianPolicy(
            hidden_sizes=hidden_sizes,
            obs_dim=obs_dim,
            action_dim=action_dim,
        ).to(device=ptu.device)

        print('Device: ', ptu.device)

        clip_value = 1.0
        for p in qf1.parameters():
            p.register_hook(lambda grad: torch.clamp(grad, -clip_value, clip_value))
        for p in qf2.parameters():
            p.register_hook(lambda grad: torch.clamp(grad, -clip_value, clip_value))
        for p in policy.parameters():
            p.register_hook(lambda grad: torch.clamp(grad, -clip_value, clip_value))

        return {'qf1' : qf1, 'qf2' : qf2, 'qf1_target' : qf1_target, 'qf2_target' : qf2_target, 'policy' : policy}

    @staticmethod
    def get_q_network(networks):
        """ Returns the q network from a dict of networks.

        This method extracts the q-network from the dictonary of networks
        created by the function create_networks.

        Args:
            networks: Dict containing the networks.

        Returns:
            The q-network as torch object.
        """
        return networks['qf1']

    @staticmethod
    def get_policy_network(networks):
        """ Returns the policy network from a dict of networks.

        This method extracts the policy network from the dictonary of networks
        created by the function create_networks.

        Args:
            networks: Dict containing the networks.

        Returns:
            The policy network as torch object.
        """
        return networks['policy']
    

