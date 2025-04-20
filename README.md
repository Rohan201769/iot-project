# WSN Routing Protocol Simulation

This project provides a framework for simulating and comparing energy-efficient routing protocols in Wireless Sensor Networks (WSNs).

## Overview

The simulation framework allows for the evaluation of different routing protocols based on metrics such as:
- Network lifetime
- Energy consumption
- Packet delivery rate
- Energy efficiency

## Implemented Routing Protocols

1. **LEACH (Low-Energy Adaptive Clustering Hierarchy)**
   - Hierarchical routing protocol
   - Forms clusters with cluster heads responsible for data aggregation
   - Rotates cluster head role to balance energy consumption

2. **Directed Diffusion**
   - Query-based protocol
   - Uses interest propagation and gradient establishment
   - Path reinforcement based on data delivery performance

3. **GEAR (Geographic and Energy Aware Routing)**
   - Location-based protocol
   - Considers both geographic progress and energy consumption for routing
   - Defines target regions for sensor queries

4. **PEGASIS (Power-Efficient Gathering in Sensor Information Systems)**
   - Chain-based hierarchical protocol
   - Forms a chain of sensor nodes for data relaying
   - Rotates leader role for transmitting to the base station

## Project Structure

```
wsn_simulation/
├── config/                # Configuration settings
├── core/                  # Core simulation components
├── protocols/             # Routing protocol implementations
├── utils/                 # Utility functions and classes
├── experiments/           # Experiment scripts
└── output/                # Simulation results and visualizations
```

## Requirements

- Python 3.7+
- Required libraries:
  - numpy
  - matplotlib
  - networkx
  - simpy
  - pandas

Install dependencies with:
```
pip install numpy matplotlib networkx simpy pandas
```

## Usage

### Basic Usage

Run a simple comparison of all protocols:

```
python main.py
```

### Custom Configuration

Specify network size and simulation time:

```
python main.py --nodes 200 --time 1500
```

### Select Specific Protocols

Compare only selected protocols:

```
python main.py --protocols LEACH PEGASIS
```

### Use Predefined Configurations

```
python main.py --config small
python main.py --config large
python main.py --config high_traffic
```

### Run Specific Experiments

```
python experiments/energy_efficiency_test.py
python experiments/network_scalability_test.py
```

## Extending the Framework

### Adding a New Protocol

1. Create a new file in the `protocols/` directory
2. Extend the `RoutingProtocol` base class
3. Implement the required methods
4. Update the protocol initialization in `core/simulation.py`

### Creating New Experiments

1. Create a new script in the `experiments/` directory
2. Use the `WSNSimulation` class to run simulations
3. Use the `MetricsAnalyzer` and `WSNVisualizer` classes to analyze and visualize results

## Visualization Examples

The framework generates various visualizations to help analyze protocol performance:

- Network topology diagrams
- Alive nodes over time charts
- Energy consumption comparisons
- Performance metrics across different scenarios

## References

This project is based on the following research paper:

- Pantazis, N.A., Nikolidakis, S.A. and Vergados, D.D., 2013. Energy-efficient routing protocols in wireless sensor networks: A survey. IEEE Communications Surveys & Tutorials, 15(2), pp.551-591.