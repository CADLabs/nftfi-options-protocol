# NFTfi Options Protocol

An Options Protocol built on top of NFTfi.

## P2P Options Marketplace Model

A radCAD Options Marketplace Model

### Software Architecture

TODO: Add standard structure

### Assumptions

- The options marketplace model is a peer-to-peer agent based model for the purchase and sale of derivative instruments.
- The instruments in question are a vanilla call option, a vanilla put option, and a straddle option.
- The underlying asset is a generic volatile asset whose price evolves according to a standard Geometric Brownian Motion parameterized by a mean and a volatility parameter, changing the mean of the process allows setting bull and bear scenarios.
- The simulation runs for 365 days, with agents being able to purchase options with a one year maturity and strike price of 2000 (equal to initial volatile asset price) at any point during the simulation, provided there are options available for purchase and agents are not already engaged in an option agreement with a counterparty.
- Buy side agents <i>may</i> take the decision to exercise as soon as they are in profit.

### Analysis

A single high level analysis is performed - Final Timestep volatile asset price vs option buy and sell side PnL.
The analysis yields intutive, qualitatively useful general purpose results, showcasing the ability to use the model for analyses of the sort.

An ordinary least squares regression analysis is used in post-processing to find the line of best fit encapsulating the trend in the PnL point clouds for buy and sell side, in the scenarios taken into consideration.

#### Results

- In a bull market for Call options PnL is in favor of the buy-side of the marketplace
- In a bull market for Put options PnL is in favor of the sell-side of the marketplace
- In a bull market for Straddle options PnL it is less clear due to the risk-neutrality of the instrument, which manifests at the aggregate level

### Usage

Run each of:
- 1a_call_option_notebook
- 2a_put_option_notebook
- 3a_straddle_option_notebook

Through Cell -> Run All and inspect produced output

Parameter settings:
NOTE: These are WIP and not intended as the final UX
- Number of Agents: In /experiments/simulation_configuration.py
- Number of Monte Carlo Runs: In /experiments/simulation_configuration.py
- Market Scenario: In /model/system_params.py

### Extensions
- Agent behavior is extremely simplistic and does not capture the behavior of a rational option purchaser or seller at a level for observed dynamics to be realistic beyond a qualitative synthesis.
- The options marketplace is fully generic and does not take into account constraints of non-fungibility around NFTs as the underyling assets
- The generic underyling asset's price evolves according to a GBM, which is a simplistic assumption even for stocks in traditional models, and is more than likely inappropriate for modelling NFT prices, which are more realistically modelled ad-hoc and on a per-collection basis

## Software Architecture

See [diagrams/](diagrams/)

* Diagram X: ...

![Option Architecture Overview](diagrams/NFTfi%20Options%20Protocol%20-%20Option%20Architecture%20-%20Overview.png)

## NFTfi Protocol Contract Refactors

See https://github.com/CADLabs/nftfi-options-protocol-contracts

<Summary>
