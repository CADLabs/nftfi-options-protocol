import numpy as np
from scipy.stats import norm
from model.types import Option

import experiments.simulation_configuration as simulation

n_agents = simulation.N_AGENTS



def policy_agents(params, substep, state_history, previous_state):
    """Update Agent Behavior
    Update agent behavior
    """

    # Parameters
    dt = params["dt"]
    strike_price = params["strike_price"]
    option_maturity = params["option_maturity"]
    option_type = params["option_type"]

    # State Variables
    agents = [previous_state["agent_"+str(i)] for i in range(n_agents)]
    timestep = previous_state["timestep"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    risk_free_rate = previous_state["risk_free_rate"]
    
    # BSM Volatility
    # make this not hacky for the first few timesteps
    
    sigma = 0.1
    
    if timestep > 2:
        price_history = np.array([state[-1]["volatile_asset_price"] for state in state_history[0:timestep]])
        returns_history = price_history[1:] / price_history[:-1] - 1
        sigma = returns_history.std() * np.sqrt(option_maturity)

    option = Option(
        option_type=option_type,
        underlying_price=volatile_asset_price,
        strike_price=strike_price,
        maturity=option_maturity,
        risk_free_rate=risk_free_rate,
        volatility=sigma,
    )
    
    bsm_price = option.bsm_price(timestep)
    option_payoff = option.payoff()
    
    # Agent Logic

    p_buy = 0.05
    p_sell = 0.05
    p_exercise = 0.05
    
    for agent in agents:
        
        buy_option = np.random.binomial(1, p_buy) # 0 or 1 w probability p
        sell_option = np.random.binomial(1, p_sell) # 0 or 1 w probability p
        exercise_option = np.random.binomial(1, p_exercise) # 0 or 1 w probability p
        
        # restrict logic to have agents only buy/sell and exercise once throughout the simulation
        # can be extended
        if agent.exercised == False:
            
            # agent puts an option on the market with probability p_sell
            if (agent.option_side != "buy"
                and agent.accepting_buy_order == False
                and sell_option == 1
               ):
                
                agent.accepting_buy_order = True
        
            # agents not in possession of an option buy one with probability p_buy
            if agent.has_counterparty == False and buy_option == 1:
                
                # find an available seller amongst agents that are selling
                for sell_agent in agents:
                    
                    # buy from first available seller
                    if sell_agent.accepting_buy_order:
                        
                        # buy the option and exit seller search
                        agent.buy_option(sell_agent, timestep, bsm_price)
                        break
                        
            # check if in profit
            payoff_value = option_payoff(volatile_asset_price, strike_price)
            profit = payoff_value - agent.premium_paid
            
            is_in_profit = profit > 0

            # get agents who own the option to exercise it
            if (agent.option_side == "buy"
                and agent.has_counterparty == True
                and is_in_profit == True
                and exercise_option == 1
               ):
                
                # get the counterparty
                sell_agent = previous_state["agent_"+str(agent.bought_from_Id)]
                
                # exercise
                agent.exercise(sell_agent, option, volatile_asset_price, timestep)
            
        
            
    agent_keys = [agent.key for agent in agents]
    agent_dict = dict(zip(agent_keys,agents))
    
    return agent_dict
