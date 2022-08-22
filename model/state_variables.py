from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import numpy as np
from model.types import (
    StateVariableKey,
    Uninitialized,
    Percentage,
    APR,
    USD,
    VolatileAssetUnits,
    StableAssetUnits,
)
from model.utils import default


@dataclass
class StateVariables:
    """## State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Simulation
    timestamp: datetime = None
    """The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter."""
    volatile_asset_price: USD = 2_000
    """The Volatile Asset initial price, update by `volatile_asset_process` System Parameter in `model.parts.price_processes`."""
    discounted_payoff: USD = 0
    """ discounted payoff"""
    risk_free_rate: APR = 0.03
    """ rf"""


initial_state = StateVariables().__dict__
