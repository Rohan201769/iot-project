"""
Mobility Test
------------

This script tests protocol performance with mobile nodes.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from core.simulation import WSNSimulation
from core.node import SensorNode

# Extend Node class to support mobility
class MobileNode(SensorNode):
    """Sensor node with mobility support"""
    
    def __init__(self, env, node_id, position, initial_energy=1.0, 
                max_speed=1.0, mobility_pattern='random_walk'):
        """Initialize a mobile sensor node
        
        Args:
            env: SimPy environment
            node_id: Unique node ID
            position: Initial (x, y) position
            initial_energy: Initial energy level (0.0 to 1.0)
            max_speed: Maximum speed of node movement
            mobility_pattern: Mobility pattern ('random_walk', 'reference_point', 'static')
        """
        super().__init__(env, node_id, position, initial_energy)
        self.max_speed = max_speed
        self.mobility_pattern = mobility_pattern
        self.direction = np.random.rand() * 2 * np.pi  # Random initial direction
        self.reference_point = position  # For reference point group mobility
        self.env.process(self.move())
        
    def move(self):
        """Process for node movement"""
        while True:
            # Skip movement if node is dead
            if not self.alive:
                yield self.env.timeout(10)
                continue
                
            # Move according to mobility pattern
            if self.mobility_pattern == 'static':
                # No movement
                pass
            
            elif self.mobility_pattern == 'random_walk':
                # Random direction change
                self.direction += np.random.normal(0, 0.5)
                
                # Calculate movement
                speed = self.max_speed * np.random.rand()
                dx = speed * np.cos(self.direction)
                dy = speed * np.sin(self.direction)
                
                # Update position with boundary check
                new_x = max(0, min(self.position[0] + dx, 100))
                new_y = max(0, min(self.position[1] + dy, 100))
                self.position = (new_x, new_y)
                
            elif self.mobility_pattern == 'reference_point':
                # Move reference point
                ref_direction = np.random.rand() * 2 * np.pi
                ref_speed = self.max_speed * 0.5 * np.random.rand()
                ref_dx = ref_speed * np.cos(ref_direction)
                ref_dy = ref_speed * np.sin(ref_direction)
                
                ref_x = max(0, min(self.reference_point[0] + ref_dx, 100))
                ref_y = max(0, min(self.reference_point[1] + ref_dy, 100))
                self.reference_point = (ref_x, ref_y)
                
                # Move node around reference point
                node_direction = np.random.rand() * 2 * np.pi
                node_speed = self.max_speed * 0.2 * np.random.rand()
                node_dx = node_speed * np.cos(node_direction)
                node_dy = node_speed * np.sin(node_direction)
                
                # Update position with boundary check
                new_x = max(0, min(self.reference_point[0] + node_dx, 100))
                new_y = max(0, min(self.reference_point[1] + node_dy, 100))
                self.position = (new_x, new_y)
            
            # Update neighbors after movement
            self.update_neighbors()
            
            # Movement interval
            yield self.env.timeout(10)
    
    def update_neighbors(self):
        """Update neighbor list after movement"""
        # This method would be called by the simulation
        pass

def test_mobility(base_config, mobility_patterns, protocols=None):
    """Test protocol performance with mobile nodes
    
    Args:
        base_config: Base configuration dictionary
        mobility_patterns: List of mobility patterns to test
        protocols: List of protocol names to test
        
    Returns:
        pd.DataFrame: Results for all tests
    """
    if protocols is None:
        protocols = ["LEACH", "DirectedDiffusion", "GEAR", "PEGASIS"]
    
    # Ensure output directory exists
    os.makedirs("output/mobility_tests", exist_ok=True)
    
    results = []
    
    for protocol in protocols:
        for mobility in mobility_patterns:
            print(f"Testing {protocol} with {mobility} mobility...")
            
            # Configure simulation
            config = base_config.copy()
            config['protocol_type'] = protocol
            config['mobility_pattern'] = mobility
            
            # Run simulation (this is a placeholder - actual implementation would
            # need to modify the WSNSimulation class to support mobile nodes)
            simulation = WSNSimulation(config)
            metrics = simulation.run()
            
            # Record results
            results.append({
                'Protocol': protocol,
                'Mobility Pattern': mobility,
                'Network Lifetime': metrics['network_lifetime'],
                'Packets Delivered': metrics['packets_delivered'],
                'Total Energy Consumed': metrics['total_energy_consumed']
            })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv("output/mobility_tests/mobility_results.csv", index=False)
    
    # Create visualizations
    visualize_mobility_results(results_df)
    
    return results_df

def visualize_mobility_results(results_df):
    """Create visualizations for mobility test results
    
    Args:
        results_df: DataFrame with test results
    """
    protocols = results_df['Protocol'].unique()
    patterns = results_df['Mobility Pattern'].unique()
    
    # Bar chart for network lifetime across mobility patterns
    plt.figure(figsize=(14, 8))
    bar_width = 0.2
    x = np.arange(len(patterns))
    
    for i, protocol in enumerate(protocols):
        protocol_data = results_df[results_df['Protocol'] == protocol]
        lifetimes = [protocol_data[protocol_data['Mobility Pattern'] == pattern]['Network Lifetime'].values[0] 
                    for pattern in patterns]
        plt.bar(x + i*bar_width, lifetimes, bar_width, label=protocol)
    
    plt.title('Network Lifetime across Mobility Patterns')
    plt.xlabel('Mobility Pattern')
    plt.ylabel('Network Lifetime (time units)')
    plt.xticks(x + bar_width * (len(protocols)-1)/2, patterns)
    plt.legend()
    plt.savefig("output/mobility_tests/network_lifetime_mobility.png")
    
    # Bar chart for packets delivered across mobility patterns
    plt.figure(figsize=(14, 8))
    
    for i, protocol in enumerate(protocols):
        protocol_data = results_df[results_df['Protocol'] == protocol]
        packets = [protocol_data[protocol_data['Mobility Pattern'] == pattern]['Packets Delivered'].values[0] 
                  for pattern in patterns]
        plt.bar(x + i*bar_width, packets, bar_width, label=protocol)
    
    plt.title('Packets Delivered across Mobility Patterns')
    plt.xlabel('Mobility Pattern')
    plt.ylabel('Packets Delivered')
    plt.xticks(x + bar_width * (len(protocols)-1)/2, patterns)
    plt.legend()
    plt.savefig("output/mobility_tests/packets_delivered_mobility.png")

# Note: This test is a placeholder - to fully implement mobility testing, 
# the simulation framework would need to be extended to handle mobile nodes

if __name__ == "__main__":
    from config.simulation_config import get_config
    
    # Get base configuration
    config = get_config('medium')
    
    # Define mobility patterns to test
    mobility_patterns = ['static', 'random_walk', 'reference_point']
    
    print("Note: Mobility testing requires extending the simulation framework.")
    print("This script is provided as a template for future implementation.")