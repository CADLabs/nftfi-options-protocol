import model.parts.options as options
import model.parts.agents as agents
import experiments.simulation_configuration as simulation

from model.utils import update_from_signal, update_timestamp

n_agents = simulation.N_AGENTS

enabled = "enabled"
description = "description"
policies = "policies"
variables = "variables"

state_update_blocks = [
    # Run first
    {
        description: """
            Update volatile asset price
        """,
        policies: {}, # Ignore for now
        # State variables
        variables: {
            'volatile_asset_price': options.update_volatile_asset_price,
        }
    },
    {
        description: """
            Update option payoff
        """,
        policies: {}, # Ignore for now
        # State variables
        variables: {
            'discounted_payoff': options.update_discounted_payoff,
        }
    },
    {
        description: """
            Agent shenanigans
        """,
        policies: {
            "agent_actions": agents.policy_agents,
        },
        variables: {
            key: update_from_signal(key)
            for key in ["agent_"+str(i) for i in range(n_agents)]
        },
    },
]
