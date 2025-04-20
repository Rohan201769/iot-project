"""
WSN Routing Protocol Simulation
-------------------------------

This script runs simulations to compare different routing protocols in Wireless Sensor Networks.
"""

import argparse
import sys
from config.simulation_config import get_config
from experiments.compare_protocols import compare_protocols
from core.simulation import WSNSimulation

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
                        
    parser.add_argument('--visual', action='store_true',
                        help='Run visual simulation')
                        
    parser.add_argument('--save-animation', action='store_true',
                        help='Save animation to file (only works with --visual)')
    
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
    else:
        protocols = ['LEACH', 'DirectedDiffusion', 'GEAR', 'PEGASIS']
    
    if args.visual:
        # Load visualization module only when needed
        try:
            from utils.visual_simulation import WSNVisualSimulation
        except ImportError:
            print("Error: Could not import visualization module.")
            print("Make sure utils/visual_simulation.py exists and contains the WSNVisualSimulation class.")
            sys.exit(1)
            
        # Run visual simulation for each selected protocol
        for protocol in protocols:
            print(f"Starting visual simulation using {protocol} protocol...")
            
            # Configure simulation for this protocol
            protocol_config = config.copy()
            protocol_config['protocol_type'] = protocol
            
            # Create simulation instance
            simulation = WSNSimulation(protocol_config)
            
            # Run the visual simulation
            visual_sim = WSNVisualSimulation(simulation)
            try:
                visual_sim.start(save_animation=args.save_animation)
            except Exception as e:
                print(f"Error during visualization of {protocol}: {str(e)}")
                print("Trying next protocol...")
    else:
        # Run normal comparison
        print(f"Starting simulation with {config['num_nodes']} nodes for {config['simulation_time']} time units")
        
        # Run protocol comparison
        analyzer = compare_protocols(config, protocols)
        
        print("\nSimulation complete. Results saved to output/ directory.")

if __name__ == "__main__":
    main()