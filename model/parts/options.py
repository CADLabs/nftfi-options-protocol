# +
import numpy as np
import typing

from model.types import (
    USD,
)
from model.system_parameters import Parameters
# -

import experiments.simulation_configuration as simulation

timesteps = simulation.TIMESTEPS


def update_volatile_asset_price(
    params, substep, state_history, previous_state, policy_input
):
    """Update Volatile Asset Price
    Update the volatile asset price from the `volatile_asset_price_process`.
    """

    # Parameters
    dt = params["dt"]
    volatile_asset_price_process = params["volatile_asset_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the price sample for the current run and timestep
    volatile_asset_price_sample = volatile_asset_price_process(run, timestep * dt)

    return "volatile_asset_price", volatile_asset_price_sample


def update_discounted_payoff(
    params, substep, state_history, previous_state, policy_input
):
    """Update Volatile Asset Price
    Update the volatile asset price from the `volatile_asset_price_process`.
    """

    # Parameters
    dt = params["dt"]
    volatile_asset_price_process = params["volatile_asset_price_process"]
    option_maturity = params["option_maturity"]
    strike_price = params["strike_price"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    
    volatile_asset_price = previous_state["volatile_asset_price"]
    risk_free_rate = previous_state["risk_free_rate"]

    rf_daily = risk_free_rate / (timesteps * dt)
    d_payoff = max(volatile_asset_price - strike_price, 0) * np.exp(-rf_daily* (option_maturity - timestep))

    return "discounted_payoff", d_payoff
