import numpy as np
from scipy.stats import norm
from model.types import Option

n_agents = 100



def policy_agents(params, substep, state_history, previous_state):
    """Update Agent Behavior
    Update agent behavior
    """

    # Parameters
    dt = params["dt"]
    strike_price = params["strike_price"]
    option_maturity = params["option_maturity"]

    # State Variables
    agents = [previous_state["agent_"+str(i)] for i in range(n_agents)]
    timestep = previous_state["timestep"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    risk_free_rate = previous_state["risk_free_rate"]
    
    # BSM Volatility
    # make this not hacky for the first few timesteps
    
    sigma = 0.01
    
    if timestep > 2:
        price_history = np.array([state[-1]["volatile_asset_price"] for state in state_history[0:timestep]])
        returns_history = price_history[1:] / price_history[:-1] - 1
        sigma = returns_history.std() * np.sqrt(timestep)


    option = Option(
        option_type="call",
        underlying_price=volatile_asset_price,
        strike_price=strike_price,
        maturity=option_maturity,
        risk_free_rate=risk_free_rate,
        volatility=sigma,
    )
    
    option_payoff = option.option_payoff()
    bsm_price = 0#option.bsm_price(timestep)
    
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
            if agent.is_selling_option == False and sell_option == 1:
                agent.is_selling_option = True
        
            # agents not in possession of an option buy one with probability p_buy
            if agent.has_active_option == False and buy_option == 1:
                
                # find an available seller amongst agents that are selling
                for sell_agent in agents:
                    
                    # buy from first available seller
                    if sell_agent.is_selling_option:
                        
                        # buy the option and exit seller search
                        agent.buy_option(sell_agent, timestep, bsm_price)
                        break

            # get agents who own the option to exercise it
            if agent.option_side == "buy" and agent.has_active_option == True and exercise_option == 1:
                    
                # get the counterparty
                sell_agent = previous_state["agent_"+str(agent.bought_from_Id)]
                
                # exercise
                agent.exercise(sell_agent, volatile_asset_price, strike_price, option_maturity, timestep, option_payoff)
            
        
            
    agent_keys = [agent.key for agent in agents]
    agent_dict = dict(zip(agent_keys,agents))
    
    return agent_dict
