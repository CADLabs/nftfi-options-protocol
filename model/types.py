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
    
    # base

    agent_id: str
    """Agent ID"""
    
    _option_side: str = None
    """Option side"""
    
    _has_counterparty: bool = False
    """Agent is currently engaged in option"""
    
    _underwrittenAt: int = None
    """Timestep when option was underwritten between buyer and seller"""
    
    _time_held: int = 0
    """Time difference between bought and exercised"""
    
    # buy side
    
    _bought_from_Id: str = None
    """Id of option seller"""
    
    _option_bought_at: int = None
    """Time at which buyer bought"""
    
    _premium_paid: float = 0.0
    """Premium buyer paid"""
    
    _exercised: bool = False
    """If option is exercised"""
    
    _exercisedAt: int = None
    """Timestep of option exercise"""
    
    _payoff_received: USD = 0.0
    """Current value of payoff for option"""
    
    _discounted_payoff_received: USD = 0.0
    """Present (T0) value of payoff for option"""
    
    # sell side
    
    _sold_to_Id: str = None
    """Id of option buyer"""
    
    _option_sold_at: int = None
    """Time at which seller sold"""
    
    _accepting_buy_order: bool = False
    """Agent is currently short an option"""
    
    _premium_received: float = 0.0
    """Premium seller received"""
    
    _payoff_paid: USD = 0.0
    """Current value of payoff for option"""
    
    _discounted_payoff_paid: USD = 0.0
    """Present (T0) value of payoff for option"""

    
    def buy_option(self, sell_agent, timestep, premium):
        """
        Buy option
        """
        
        # buy and sell side recording
        self.option_side = "buy"
        sell_agent.option_side = "sell"
        
        self.bought_from_Id = sell_agent.agent_ID
        sell_agent.sold_to_Id = self.agent_ID
        
        # buy side
        self.has_counterparty = True
        self.underwrittenAt = timestep
        self.option_bought_at = timestep
        self.premium_paid = premium
        
        #sell side
        sell_agent.has_counterparty = True
        sell_agent.underwrittenAt = timestep
        sell_agent.option_sold_at = timestep
        sell_agent.premium_received = premium
        
        sell_agent.accepting_buy_order = False

        return self
    
    def exercise(self, sell_agent, option, asset_price: USD, timestep: int):
        """
        Exercise an owned option
        """
        
        assert timestep <= option.maturity, 'exercising expired option'
        assert sell_agent.agent_ID == self.bought_from_Id, 'buyer and seller mismatch'
        
        # instantiate payoff function
        option_payoff = option.payoff()
        
        # get discount factor
        discount_factor = np.exp(-option.risk_free_rate*((option.maturity-timestep)/365))
        
        # buy side
        self.payoff_received = option_payoff(asset_price, option.strike_price)
        self.discounted_payoff_received = discount_factor * self.payoff_received

        self.exercised = True
        self.exercisedAt = timestep
        self.time_held = timestep - self.underwrittenAt
        self.option_side = None
        self.has_counterparty = False
        
        # sell side
        sell_agent.payoff_paid = option_payoff(asset_price, option.strike_price)
        sell_agent.discounted_payoff_paid = discount_factor * sell_agent.payoff_paid
        # mark seller also as exercised to exclude from further interactions
        sell_agent.exercised = True 
        sell_agent.exercisedAt = timestep
        sell_agent.time_held = timestep - self.underwrittenAt
        sell_agent.option_side = None
        sell_agent.has_counterparty = False

        return self


    @property
    def key(self) -> str:
        return "_".join(["agent", self.agent_id])
    
    @property
    def agent_ID(self):
        """Agent ID"""
        return self.agent_id

    @property
    def has_counterparty(self):
        """Option is owned"""
        return self._has_counterparty
    
    @has_counterparty.setter
    def has_counterparty(self, v: bool) -> None:
        self._has_counterparty = v
    
    @property
    def exercised(self):
        """Option has been exercised"""
        return self._exercised
    
    @exercised.setter
    def exercised(self, v: bool) -> None:
        self._exercised = v
        
    @property
    def exercisedAt(self):
        """Option has been exercised"""
        return self._exercisedAt
    
    @exercised.setter
    def exercisedAt(self, v: int) -> None:
        self._exercisedAt = v
        
    @property
    def underwrittenAt(self):
        """Option has been activated"""
        return self._underwrittenAt
    
    @exercised.setter
    def underwrittenAt(self, v: int) -> None:
        self._underwrittenAt = v
    
    @property
    def time_held(self):
        """Time exercised option was held"""
        return self._time_held
    
    @time_held.setter
    def time_held(self, v: int) -> None:
        self._time_held = v

    @property
    def payoff_received(self):
        """Current value of payoff for option"""
        return self._payoff_received
    
    @payoff_received.setter
    def payoff_received(self, v: USD) -> None:
        self._payoff_received = v

    @property
    def discounted_payoff_received(self):
        """Present (T0) value of payoff for option"""
        return self._discounted_payoff_received
    
    @discounted_payoff_received.setter
    def discounted_payoff_received(self, v: USD) -> None:
        self._discounted_payoff_received = v
        
    @property
    def payoff_paid(self):
        """Current value of payoff for option"""
        return self._payoff_paid
    
    @payoff_paid.setter
    def payoff_paid(self, v: USD) -> None:
        self._payoff_paid = v

    @property
    def discounted_payoff_paid(self):
        """Present (T0) value of payoff for option"""
        return self._discounted_payoff_paid
    
    @discounted_payoff_paid.setter
    def discounted_payoff_paid(self, v: USD) -> None:
        self._discounted_payoff_paid = v
    
    @property
    def premium_paid(self):
        """Premium paid by buyer"""
        return self._premium_paid
    
    @premium_paid.setter
    def premium_paid(self, v: USD) -> None:
        self._premium_paid = v
        
    @property
    def premium_received(self):
        """Premium recieved by seller"""
        return self._premium_received
    
    @premium_received.setter
    def premium_received(self, v: USD) -> None:
        self._premium_received = v
        
    @property
    def accepting_buy_order(self):
        """Option is owned"""
        return self._accepting_buy_order
    
    @accepting_buy_order.setter
    def accepting_buy_order(self, v: bool) -> None:
        self._accepting_buy_order = v
        
    @property
    def option_side(self):
        """Option side"""
        return self._option_side
    
    @option_side.setter
    def option_side(self, v: str) -> None:
        self._option_side = v
        
    @property
    def option_bought_at(self):
        """Option bought at"""
        return self._option_bought_at
    
    @option_bought_at.setter
    def option_bought_at(self, v: int) -> None:
        self._option_bought_at = v
        
    @property
    def option_sold_at(self):
        """Option sold at"""
        return self._option_sold_at
    
    @option_sold_at.setter
    def option_sold_at(self, v: int) -> None:
        self._option_sold_at = v
        
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
    
    @sold_to_Id.setter
    def sold_to_Id(self, v: str) -> None:
        self._sold_to_Id = v


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
        return (np.log(S/K)+(r+sigma**2/2.)*((T-t+1)/365))/(sigma*np.sqrt((T-t+1)/365))

    def d2(self, S, K, T, r, sigma, t):
        """
        BSM d2
        """
        return (np.log(S/K)+(r-sigma**2/2.)*((T-t+1)/365))/(sigma*np.sqrt((T-t+1)/365))


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
                    K*np.exp(-r*((T-t+1)/365))*norm.cdf(self.d2(S,K,T,r,sigma,t)))
        
        if self.option_type == "put":
            return (K*np.exp(-r*((T-t+1)/365))*norm.cdf(-self.d2(S,K,T,r,sigma,t))-
                    S*norm.cdf(-self.d1(S,K,T,r,sigma,t)))
        
        if self.option_type == "straddle":
            return (S*(norm.cdf(self.d1(S,K,T,r,sigma,t)) - norm.cdf(-self.d1(S,K,T,r,sigma,t))) -
                   K*np.exp(-r*((T-t+1)/365))*(norm.cdf(self.d2(S,K,T,r,sigma,t)) - norm.cdf(-self.d2(S,K,T,r,sigma,t))))
        
        return 0
    
    def payoff(self):
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
