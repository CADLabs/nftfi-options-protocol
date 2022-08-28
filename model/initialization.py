# +
"""# Initialization Module
"""

import radcad as radcad
import logging
from dataclasses import make_dataclass
from model.state_variables import StateVariables
from model.system_parameters import agent_keys
from model.types import (
    Agent,
)


def setup_initial_state(context: radcad.Context):
    """## Initial State Setup
    A function, used in the radCAD `before_subset` hook in `experiments.default_experiment`,
    that sets up the Initial State of the model from the relevant System Parameters before each simulation execution.

    This allows one to sweep the Initial State using System Parameters.
    """
    logging.info("Setting up initial state")

    params = context.parameters
    run = context.run
    timestep = 0

    StateVariablesWithAgents = make_dataclass(
        "StateVariablesWithAgents",
        fields=(
            [(key, Agent, params["agents"][key]) for key in agent_keys]
        ),
        bases=(StateVariables,),
    )
    context.initial_state.update(StateVariablesWithAgents().__dict__)
    initial_state = context.initial_state
