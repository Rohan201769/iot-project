"""
Visual WSN Simulation
--------------------

This script runs a visual simulation of WSN routing protocols.
"""

import argparse
from config.simulation_config import get_config
from core.simulation import WSNSimulation
from utils.simple_visual import SimpleWSNVisualizer

def main():
    """Run a visual simulation of WSN routing protocols"""
    parser = argparse.ArgumentParser(description='Visual simulation of WSN routing protocols')
    
    parser.add_argument('--protocol', type=str, 
                        choices=['LEACH', 'DirectedDiffusion', 'GEAR', 'PEGASIS'],
                        default='LEACH', 
                        help='Protocol to simulate')
    
    parser.add_argument('--nodes', type=int, default=50,
                        help='Number of sensor nodes')
    
    parser.add_argument('--time', type=int, default=500,
                        help='Simulation time')
    
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
                        
    parser.add_argument('--save', action='store_true',
                        help='Save animation to file')
    
    args = parser.parse_args()
    
    # Configure simulation
    config = {
        'width': 100,
        'height': 100,
        'num_nodes': args.nodes,
        'base_station_pos': (50, 50),
        'protocol_type': args.protocol,
        'simulation_time': args.time,
        'seed': args.seed
    }
    
    print(f"Starting visual simulation of {args.protocol} with {args.nodes} nodes...")
    
    # Create and run simulation
    simulation = WSNSimulation(config)
    
    # Start visualization
    visualizer = SimpleWSNVisualizer(simulation)
    visualizer.start(save_animation=args.save)
    
    print("Simulation complete.")

if __name__ == "__main__":
    main()