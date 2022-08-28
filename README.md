# NFTfi Options Protocol Hackathon Submission

A hack entry for the Macro Hacks NFT Finance Hackathon.

R&D of an Options Protocol that leverages NFTfi, for bounty number 2: "Design an options protocol around NFTfi’s inventory (i.e. the NFTs allowed on NFTfi) which settles on NFTfi."

## Table of Contents

* [Directory Structure](#Directory-Structure)
* [P2P Options Marketplace Model](#P2P-Options-Marketplace-Model)
* [NFTfi Options Protocol Software Architecture](#NFTfi-Options-Protocol-Software-Architecture)
* [NFTfi Protocol Contract Refactors](#NFTfi-Protocol-Contract-Refactors)

## Directory Structure

* [contracts/](contracts/): A Git submodule containing a fork and refactors of the NFTfi protocol smart contracts
* [diagrams/](diagrams/): Various diagrams created to describe the software architecture and option protocol R&D
* [experiments/](experiments/): Analysis notebooks and experiment workflow (such as configuration and execution)
* [model/](model/): Model software architecture (structural and configuration modules)

## P2P Options Marketplace Model

A radCAD Options Marketplace Model

### Model Architecture

The [model/](model/) directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

#### Structural Modules

The model is composed of two structural modules in the [model/parts/](model/parts/) directory: `agents.py` and `options.py`.

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model, e.g. number of epochs in a year, Gwei in 1 Ether |
| [initialization.py](model/initialization.py) | Code used to set up the Initial State of the model before each subset from the System Parameters |
| [state_update_blocks.py](model/state_update_blocks.py) | radCAD model State Update Block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various Python types used in the model, such as the `Stage` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

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

### Environment Setup

The following steps guide you through how to set up a custom development environment using Python 3 and Jupyter.

Please note the following prerequisites before getting started:
* Python: tested with versions 3.8, 3.9
* NodeJS might be needed if using Plotly with Jupyter Lab (Plotly works out the box when using the Anaconda/Conda package manager with Jupyter Lab or Jupyter Notebook)

First, set up a Python 3 [virtualenv](https://docs.python.org/3/library/venv.html) development environment (or use the equivalent Anaconda step):
```bash
# Create a virtual environment using Python 3 venv module
python3 -m venv venv
# Activate virtual environment
source venv/bin/activate
```

Make sure to activate the virtual environment before each of the following steps.

Secondly, install the Python 3 dependencies using [Pip](https://packaging.python.org/tutorials/installing-packages/), from the [requirements.txt](requirements.txt) file within your new virtual environment:
```bash
# Install Python 3 dependencies inside virtual environment
pip install -r requirements.txt
```

To create a new Jupyter Kernel specifically for this environment, execute the following command:
```bash
python3 -m ipykernel install --user --name python-radcad --display-name "Python (radCAD Model)"
```

You'll then be able to select the kernel with display name `Python (radCAD Model)` to use for your notebook from within Jupyter.

To start Jupyter Notebook or Lab (see notes about issues with [using Plotly with Jupyter Lab](#Known-Issues)):
```bash
jupyter notebook
# Or:
jupyter lab
```

For more advanced Unix/macOS users, a [Makefile](Makefile) is also included for convenience that simply executes all the setup steps. For example, to setup your environment and start Jupyter Lab:
```bash
# Setup environment
make setup
# Start Jupyter Lab
make start-lab
```

### Experiment Execution

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

## NFTfi Options Protocol Software Architecture

See [diagrams/](diagrams/):
* [NFTfi Options Protocol - NFTfi Loan Agreement.pdf](diagrams/NFTfi%20Options%20Protocol%20-%20NFTfi%20Loan%20Agreement.pdf): Deconstruction of the existing NFTfi loan agreement type to understand how one would wire up a new option agreement type
* [NFTfi Options Protocol - NFTfi Loan Life Cycle.pdf](diagrams/NFTfi%20Options%20Protocol%20-%20NFTfi%20Loan%20Life%20Cycle.pdf): Deconstruction of the existing NFTfi loan agreement type to understand how one would wire up a new option agreement type
* [NFTfi Options Protocol - Vanilla Options.pdf](diagrams/NFTfi%20Options%20Protocol%20-%20Vanilla%20Options.pdf): Analysis of how settlement of vanilla put options compares to using NFTfi loans as primitive put options
* [NFTfi Options Protocol - Option Architecture - *.pdf](diagrams/NFTfi%20Options%20Protocol%20-%20Option%20Architecture%20-%20Overview.pdf): Architecting a NFTfi Option agreement type based on Putty v2

![Option Architecture Overview](diagrams/NFTfi%20Options%20Protocol%20-%20Option%20Architecture%20-%20Overview.png)

## NFTfi Protocol Contract Refactors

See https://github.com/CADLabs/nftfi-options-protocol-contracts
