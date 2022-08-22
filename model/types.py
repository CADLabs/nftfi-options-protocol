# +
"""# Types
Various Python types used in the model
"""

import numpy as np
import sys

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass
from enforce_typing import enforce_types
from typing import Union, List, Dict
from abc import ABCMeta, abstractmethod
from datetime import datetime
from scipy.stats import norm

# If Python version is greater than equal to 3.8, import from typing module
# Else also import from typing_extensions module
if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable, NamedTuple
else:
    from typing import List, NamedTuple
    from typing_extensions import TypedDict, Callable


# Generic types
Uninitialized = np.nan
Percentage = float
APR = float

# Simulation types
Timestep = int
Run = int
StateVariableKey = str

# Assets
USD = Union[int, float]
VolatileAssetUnits = Union[int, float]
StableAssetUnits = Union[int, float]


@enforce_types
@dataclass(frozen=False)
class Agent(metaclass=ABCMeta):
    """## Generic Deposit
    A generic option agent
    """

    agent_id: str
    """Agent ID"""
    _has_active_option: bool = False
    """Agent is currently engaged in option"""
    _owned_activatedAt: int = None
    """Timestep when option was purchased"""
    _premium_paid: float = 0.0
    """Premium paid"""
    _exercised: bool = False
    """If option is exercised"""
    _exercisedAt: int = None
    """Timestep of option exercise"""
    _time_held: int = 0
    """Time difference between bought and exercised"""
    _payoff_value: USD = 0.0
    """Current value of payoff for option"""
    _discounted_payoff_value: USD = 0.0
    """Present (T0) value of payoff for option"""

    # Sell side
    _option_side: str = None
    """Option side"""
    _is_selling_option: bool = False
    """Agent is currently long an option"""
    _option_sold_at: int = None
    """Agent is currently long an option"""
    
    _sold_to_Id: str = None
    """Id of option buyer"""
    
    _bought_from_Id: str = None
    """Id of option seller"""
    
    
    def buy_option(self, sell_agent, timestep, premium):
        """
        Buy option
        """
        self._has_active_option = True
        self._owned_activatedAt = timestep
        self._premium_paid = premium
        
        # buy and sell side recording
        self.option_side = "buy"
        sell_agent.option_side = "sell"
        
        self.bought_from_Id = sell_agent.agent_ID
        sell_agent.sold_to_Id = self.agent_ID

        return self
    
    def exercise(self, sell_agent, asset_price: USD, strike_price: USD, option_maturity: int, timestep: int, payoff):
        """
        Exercise an owned option
        """
        
        assert timestep <= option_maturity, 'exercising expired option'
        assert sell_agent.agent_ID == self.bought_from_Id, 'buyer and seller mismatch'
        
        self._payoff_value = payoff(asset_price, strike_price)
        self._has_active_option = False
        self._exercised = True
        self._exercisedAt = timestep
        self._time_held = timestep - self._owned_activatedAt
        self._option_side = None
        
        # mark seller also as exercised to exclude from further interactions
        sell_agent.exercised = True 
        sell_agent.is_selling_option = False
        sell_agent.option_side = None
        
        # TBA with setters
        # TBA: counterparty accounting consistency
        
#         sell_agent._payoff_value = -payoff(asset_price, strike_price)
#         sell_agent._has_active_option = False

#         sell_agent._exercisedAt = timestep
#         sell_agent._time_held = timestep - self._owned_activatedAt

        return self


    @property
    def key(self) -> str:
        return "_".join(["agent", self.agent_id])
    
    @property
    def agent_ID(self):
        """Agent ID"""
        return self.agent_id

    @property
    def has_active_option(self):
        """Option is owned"""
        return self._has_active_option
    
    @property
    def exercised(self):
        """Option has been exercised"""
        return self._exercised
    
    @property
    def time_held(self):
        """Time exercised option was held"""
        return self._time_held

    @property
    def payoff_value(self):
        """Current value of payoff for option"""
        return self._payoff_value

    @property
    def discounted_payoff_value(self):
        """Present (T0) value of payoff for option"""
        return self._discounted_payoff_value

    @has_active_option.setter
    def has_active_option(self, v: bool) -> None:
        self._has_active_option = v
        
    @exercised.setter
    def exercised(self, v: bool) -> None:
        self._has_active_option = v
        
    # Sell side
    @property
    def is_selling_option(self):
        """Option is owned"""
        return self._is_selling_option
    
    @is_selling_option.setter
    def is_selling_option(self, v: bool) -> None:
        self._is_selling_option = v
        
    @property
    def option_side(self):
        """Option side"""
        return self._option_side
    
    @option_side.setter
    def option_side(self, v: str) -> None:
        self._option_side = v
        
    @property
    def bought_from_Id(self):
        """Id of seller"""
        return self._bought_from_Id
    
    @bought_from_Id.setter
    def bought_from_Id(self, v: str) -> None:
        self._bought_from_Id = v
        
    @property
    def sold_to_Id(self):
        """Id of buyer"""
        return self._sold_to_Id
    
    @bought_from_Id.setter
    def sold_to_Id(self, v: str) -> None:
        self._sold_to_Id = v
        
#     @owned_activatedAt.setter
#     def owned_activatedAt(self, timestep: int) -> None:
#         self._owned_activatedAt = timestep
# -

@enforce_types
@dataclass(frozen=False)
class Option(metaclass=ABCMeta):
    """## Generic Deposit
    A generic option buy side agent
    """

    option_type: str
    """Option type"""
    underlying_price: USD = 0.0
    """Underlying Price"""
    strike_price: USD = 0.0
    """Option Strike Price"""
    maturity: USD = 0.0
    """Option Maturity"""
    risk_free_rate: APR = 0.0
    """Risk Free Rate"""
    volatility: float = 0.0
    """Option Imp Vol"""
    
    def d1(self, S, K, T, r, sigma, t):
        """
        BSM d1
        """
        return (np.log(S/K)+(r+sigma**2/2.)*(T-t))/(sigma*np.sqrt(T-t))

    def d2(self, S, K, T, r, sigma, t):
        """
        BSM d2
        """
        return (np.log(S/K)+(r-sigma**2/2.)*(T-t))/(sigma*np.sqrt(T-t))


    def bsm_price(self, t):
        """
        BSM option price
        """
        
        S = self.underlying_price
        K = self.strike_price
        T = self.maturity 
        r = self.risk_free_rate 
        sigma = self.volatility 

        if self.option_type == "call":
            return (S*norm.cdf(self.d1(S,K,T,r,sigma,t))-
                    K*np.exp(-r*(T-t))*norm.cdf(self.d2(S,K,T,r,sigma,t)))
        
        if self.option_type == "put":
            return (K*np.exp(-r*(T-t))*norm.cdf(-self.d2(S,K,T,r,sigma,t))-
                    S*norm.cdf(-self.d1(S,K,T,r,sigma,t)))
        
        if self.option_type == "straddle":
            return (S*(norm.cdf(self.d1(S,K,T,r,sigma,t)) - norm.cdf(-self.d1(S,K,T,r,sigma,t))) -
                   K*np.exp(-r*(T-t))*(norm.cdf(self.d2(S,K,T,r,sigma,t)) - norm.cdf(-self.d2(S,K,T,r,sigma,t))))
        
        return 0
    
    def option_payoff(self):
        """
        Option payoff
        """
        
        if self.option_type == "call":
            return lambda S, K: max(S-K,0)
        
        if self.option_type == "put":
            return lambda S, K: max(K-S,0)
        
        if self.option_type == "straddle":
            return lambda S, K: abs(S-K)
    
        return lambda S, K: 0
