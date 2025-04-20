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
    
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Simulation speed multiplier')
    
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
    print("This visualization shows:")
    print("  - Node states (cluster heads, regular nodes, dead nodes)")
    print("  - Data transmissions between nodes")
    print("  - Protocol-specific behaviors:")
    
    if args.protocol == 'LEACH':
        print("    * Cluster formation with boundaries")
        print("    * Cluster head rotation")
        print("    * Data collection and aggregation")
    elif args.protocol == 'PEGASIS':
        print("    * Chain formation for efficient routing")
        print("    * Leader selection for transmitting to base station")
    elif args.protocol == 'DirectedDiffusion':
        print("    * Interest propagation from sink")
        print("    * Gradient establishment")
        print("    * Data delivery along reinforced paths")
    elif args.protocol == 'GEAR':
        print("    * Geographic target regions")
        print("    * Energy-aware geographic routing")
    
    # Create and run simulation
    simulation = WSNSimulation(config)
    
    # Start visualization
    visualizer = SimpleWSNVisualizer(simulation, interval=int(100/args.speed))
    visualizer.start(save_animation=args.save)
    
    print("Simulation complete.")

if __name__ == "__main__":
    main()