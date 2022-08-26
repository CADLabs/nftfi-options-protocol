# +
from typing import Dict, List
import experiments.simulation_configuration as simulation

import numpy as np
from operator import lt, gt
from dataclasses import dataclass
from datetime import datetime
from model.utils import default
from model.types import (
    Callable,
    Percentage,
    Timestep,
    Run,
    List,
    USD,
    APR,
    Agent,
)
from model.stochastic_processes import create_stochastic_process_realizations
# -

timesteps = simulation.TIMESTEPS
dt=simulation.DELTA_TIME

monte_carlo_runs = simulation.MONTE_CARLO_RUNS
n_agents = simulation.N_AGENTS

# Market scenario
scenario = 'Bull'

market_conditions = {
    'Bull': {
        'mu': 0.1,
        'sigma': 0.25,
    },
    'Bear': {
        'mu': -0.15,
        'sigma': 0.25,
    }
}

# +
initial_price = 2000
strike = initial_price
T = 365 * dt  # option maturity / expiration

mu = market_conditions[scenario]['mu']
sigma = market_conditions[scenario]['sigma']
# -

volatile_asset_price_samples = create_stochastic_process_realizations(
    "manual_gbm_process",#"geometric_brownian_motion_process",
    timesteps=timesteps,
    dt=dt,
    mu=mu,
    sigma=sigma,
    initial_price=initial_price,
    runs=monte_carlo_runs,
)

# +
agent_sweep = [
    [Agent(agent_id=str(i)) for i in range(n_agents)],
]

# Generate Agent Deposit IDs
agent_sweep = [
    {agent.key: agent for agent in distribution}
    for distribution in agent_sweep
]
agent_keys = list(agent_sweep[0].keys())


# -

@dataclass
class Parameters:
    """## System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value
    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Time parameters
    dt: List[Timestep] = default([simulation.DELTA_TIME])
    """
    Simulation timescale / timestep unit of time, in days.
    Used to scale calculations that depend on the number of days that have passed.
    For example, for dt = 100, each timestep equals 100 days.
    By default set to 1 day.

    NOTE Model has not been tested for `DELTA_TIME` != 1, further validation of calculations would be required.
    """

    date_start: List[datetime] = default(
        [
            datetime.now(),
        ]
    )
    """
    Start date for simulation as Python datetime

    Used by `model.utils` `update_timestamp(...)` State Update Function.
    """

    volatile_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: volatile_asset_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the volatile asset spot price at each timestep.

    By default set to a Brownian meander stochastic process.

    Used in `model.parts.price_processes`.
    """
    
    option_maturity: List[int] = default([T])
    """
    Option Maturity
    """
    
    strike_price: List[int] = default([strike])
    """
    Option Strike Price
    """
    
    option_type: List[str] = default(["call"])
    """
    Option Type, put, call or straddle
    """
    
    # Agents configuration
    agents: List[Dict[str, Agent]] = default(agent_sweep)
    """
    The distribution of agents used to initialize the Agents State Variables,
    to enable performing a parameter sweep of the Initial State of Agents.
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
