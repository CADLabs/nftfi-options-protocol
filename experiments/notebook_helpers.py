# +
import numpy as np
import pandas as pd
from tqdm.notebook import tqdm, trange
import statsmodels.api as sm
import plotly.graph_objects as go

import experiments.simulation_configuration as simulation


# -

def check_single_agent_counterparty(df, i, run, side="buy"):
    """
    Checks if an agent has interacted with multiple counterparties throughout the simulation
    """
    
    b_flag = None
    s_flag = None
    flags_set = False
    
    counterparty_flag = False
    
    df_ = df.query('run==@run')
                
    for t in df_['timestep'].unique():
        
        t_ = t-1

        agent = df_.iloc[t_]["agent_"+str(i)]
        bought_from_id = agent._bought_from_Id
        sold_to_id = agent._sold_to_Id
        
        if side == "buy":

            if bought_from_id is not None:

                if flags_set == False:
                    b_flag = bought_from_id
                    flags_set = True

                if flags_set == True:
                    if bought_from_id != b_flag:
                        counterparty_flag = True
                        
        if side == "sell":
                    
            if sold_to_id is not None:

                if flags_set == False:
                    s_flag = sold_to_id
                    flags_set = True

                if flags_set == True:

                    if sold_to_id != s_flag:
                        counterparty_flag = True
                    
    assert counterparty_flag == False, 'agent interacted with multiple counterparties'


def check_agent_counterparty_for_run(df, n_agents, run=1, side='buy'):
        
    for i in range(n_agents):
        check_single_agent_counterparty(df, i, run, side)


def check_agent_counterparty_for_simulation(df, n_agents, subset=0, side='buy'):
        
    df_ = df.query('subset==@subset')
    
    for run in tqdm(df_['run'].unique()):
        check_agent_counterparty_for_run(df_, n_agents, run=run, side=side)


def get_KPI_for_run(df, n_agents, variable, run):
    
    L = []

    for i in range(n_agents):
        agent = df.iloc[-1]["agent_"+str(i)]
        
        L.append(getattr(agent,variable))
        
    return np.array(L)


def get_KPIs_for_run(df, n_agents, kpi_list, run):
    
    D = dict()
    
    df_ = df.query('run==@run')

    agent_fields = list(df_.iloc[-1]["agent_0"].__dict__.keys())
    
    for variable in agent_fields:
        arr = get_KPI_for_run(df_, n_agents, variable, run)
        
        D[variable] = arr
        
    D = pd.DataFrame(D)
    D = D[kpi_list]
    D['buyer_pnl'] = D['_discounted_payoff_received'] - D['_premium_paid']
    D['seller_pnl'] = D['_premium_received'] - D['_discounted_payoff_paid']
    D['final_va_price'] = df_.iloc[-1]["volatile_asset_price"]
    

    return D


def get_KPIs_for_simulation(df, n_agents, kpi_list, subset=0):
    
    L = []
    
    df_ = df.query('subset==@subset')
    
    for run in tqdm(df_['run'].unique()):
        D = get_KPIs_for_run(df_, n_agents, kpi_list, run)
        L.append(D)
        
    return L


def check_bought_or_sold_for_run(df, n_agents, run=1, timestep=-1):
    
    flag = False
    
    for i in range(n_agents):
        agent = df.query('run==@run').iloc[-1]["agent_"+str(i)]
        
        if agent._bought_from_Id is not None and agent._sold_to_Id is not None:
            print(agent.agent_id)
            flag = True
    
    return flag


def get_summary_stat_for_KPIs(L, variable):
    df_ = pd.concat([x.describe().loc[variable] for x in L], axis=1)
    df_.columns = [i for i in range(len(L))]#[variable+'_'+str(i) for i in range(len(L))]
    
    return df_.T


def get_option_payoff(df):
    
    discounted_payoffs = dict()

    for run in df["run"].unique():
        
        df_ = df.query('run == @run')

        d_payoff = df_['discounted_payoff'].iloc[-1]
        
        discounted_payoffs[run] = d_payoff
        
    return pd.DataFrame(discounted_payoffs.items(), columns=['run', 'option_payoff'])


def get_OLS_params(KPI_df, variable):
    X = KPI_df['final_va_price']
    Y = KPI_df[variable]
    X = sm.add_constant(X)
    
    model = sm.OLS(Y,X)
    results = model.fit()
    
    return results.params


def get_regression_line(KPI_df, params, variable):
    
    D = dict()
    
    for i in np.linspace(KPI_df['final_va_price'].min(), KPI_df['final_va_price'].max(), 200):
        D[i] = params[0] + params[1]*i
        
    D = pd.DataFrame(D.items())
    D.columns = ['final_va_price', variable]
    return D


def get_regression_df(KPI_df, variables):
    
    L = []
    
    for variable in variables:
        params = get_OLS_params(KPI_df, variable)
        D = get_regression_line(KPI_df, params, variable)
        L.append(D)
        
    df =  pd.concat(L, axis=1)
    df_ = df = df.loc[:,~df.columns.duplicated()].copy()
    
    return df_


def plot_agent_PnL(KPI_df, KPI_regression_df, scenario, summary_stat, option_type):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=KPI_df["final_va_price"],
            y=KPI_df['buyer_pnl'],
            mode="markers",
            name="buyer_pnl",
            line=dict(
                color="blue"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=KPI_regression_df["final_va_price"],
            y=KPI_regression_df['buyer_pnl'],
            name="buyer_pnl_fit",
            line=dict(
                color="blue"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=KPI_df["final_va_price"],
            y=KPI_df['seller_pnl'],
            mode="markers",
            name="seller_pnl",
            line=dict(
                color="red"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=KPI_regression_df["final_va_price"],
            y=KPI_regression_df['seller_pnl'],
            name="seller_pnl_fit",
            line=dict(
                color="red"
            )
        )
    )

    fig.update_layout(
        title=summary_stat+" "+option_type+" Option buyer and seller PnL across agents for all runs in a "+scenario+" scenario",
        xaxis_title="Final Asset Price",
        yaxis_title="PnL",
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.99
        )
    )

    fig.show()
