"""
WSN Routing Protocol Simulation
-------------------------------

This script runs simulations to compare different routing protocols in Wireless Sensor Networks.
"""

import argparse
from config.simulation_config import get_config
from experiments.compare_protocols import compare_protocols

def main():
    """Main entry point for WSN simulation"""
    parser = argparse.ArgumentParser(description='Simulate WSN routing protocols')
    
    parser.add_argument('--config', type=str, default=None, 
                        help='Configuration preset (small, medium, large, short, long, high_traffic, low_traffic)')
    
    parser.add_argument('--protocols', type=str, nargs='+', 
                        choices=['LEACH', 'DirectedDiffusion', 'GEAR', 'PEGASIS', 'all'],
                        default=['all'], 
                        help='Protocols to simulate')
    
    parser.add_argument('--nodes', type=int, default=None,
                        help='Number of sensor nodes')
    
    parser.add_argument('--time', type=int, default=None,
                        help='Simulation time')
    
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed')
    
    args = parser.parse_args()
    
    # Get base configuration
    config = get_config(args.config)
    
    # Override with command line arguments
    if args.nodes is not None:
        config['num_nodes'] = args.nodes
        
    if args.time is not None:
        config['simulation_time'] = args.time
        
    if args.seed is not None:
        config['seed'] = args.seed
    
    # Determine protocols to simulate
    protocols = None
    if 'all' not in args.protocols:
        protocols = args.protocols
    
    print(f"Starting simulation with {config['num_nodes']} nodes for {config['simulation_time']} time units")
    
    # Run protocol comparison
    analyzer = compare_protocols(config, protocols)
    
    print("\nSimulation complete. Results saved to output/ directory.")

if __name__ == "__main__":
    main()