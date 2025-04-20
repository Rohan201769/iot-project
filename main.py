"""
WSN Routing Protocol Simulation
-------------------------------

This script runs simulations to compare different routing protocols in Wireless Sensor Networks.
"""

import argparse
from config.simulation_config import get_config
from experiments.compare_protocols import compare_protocols
from core.simulation import WSNSimulation
from utils.visual_simulation import WSNVisualSimulation  # Import the new visualization

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
    
    if args.visual:
        # Run visual simulation with a single protocol
        protocol = args.protocols[0] if 'all' not in args.protocols else 'LEACH'
        print(f"Starting visual simulation using {protocol} protocol...")
        
        config['protocol_type'] = protocol
        simulation = WSNSimulation(config)
        
        # Fix for lifetime calculation
        simulation.metrics['first_dead_time'] = 0  # Track when first node dies
        
        # Override collect_metrics method to track first dead node
        original_collect_metrics = simulation.collect_metrics
        
        def enhanced_collect_metrics():
            while True:
                # Call the original method
                yield from original_collect_metrics()
                
                # Check for first dead node
                if simulation.metrics['first_dead_time'] == 0:
                    alive = sum(1 for node in simulation.nodes if node.alive)
                    if alive < len(simulation.nodes):
                        simulation.metrics['first_dead_time'] = simulation.env.now
                        print(f"First node died at time {simulation.env.now}")
        
        simulation.collect_metrics = enhanced_collect_metrics
        
        # Run the visual simulation
        visual_sim = WSNVisualSimulation(simulation)
        visual_sim.start(save_animation=args.save_animation)
    else:
        # Run normal comparison
        print(f"Starting simulation with {config['num_nodes']} nodes for {config['simulation_time']} time units")
        
        # Run protocol comparison
        analyzer = compare_protocols(config, protocols)
        
        print("\nSimulation complete. Results saved to output/ directory.")

if __name__ == "__main__":
    main()