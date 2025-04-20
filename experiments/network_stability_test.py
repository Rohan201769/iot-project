"""
Network Scalability Test
------------------------

This script tests how well protocols scale with increasing network size.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from core.simulation import WSNSimulation
from utils.metrics import MetricsAnalyzer

def test_scalability(base_config, network_sizes, protocols=None):
    """Test protocol scalability with varying network sizes
    
    Args:
        base_config: Base configuration dictionary
        network_sizes: List of network sizes (number of nodes) to test
        protocols: List of protocol names to test
        
    Returns:
        pd.DataFrame: Results for all tests
    """
    if protocols is None:
        protocols = ["LEACH", "DirectedDiffusion", "GEAR", "PEGASIS"]
    
    # Ensure output directory exists
    os.makedirs("output/scalability_tests", exist_ok=True)
    
    results = []
    
    for protocol in protocols:
        for num_nodes in network_sizes:
            print(f"Testing {protocol} with {num_nodes} nodes...")
            
            # Configure simulation
            config = base_config.copy()
            config['protocol_type'] = protocol
            config['num_nodes'] = num_nodes
            
            # Scale communication range with network size
            config['comm_range'] = min(30 * (num_nodes / 100)**0.25, 50)
            
            # Run simulation
            simulation = WSNSimulation(config)
            metrics = simulation.run()
            
            # Record results
            energy_per_node = metrics['total_energy_consumed'] / num_nodes
            packets_per_node = metrics['packets_delivered'] / num_nodes
            
            results.append({
                'Protocol': protocol,
                'Network Size': num_nodes,
                'Network Lifetime': metrics['network_lifetime'],
                'Packets Delivered': metrics['packets_delivered'],
                'Energy Per Node': energy_per_node,
                'Packets Per Node': packets_per_node,
                'Execution Time': metrics.get('execution_time', 0)
            })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv("output/scalability_tests/scalability_results.csv", index=False)
    
    # Create visualizations
    visualize_scalability_results(results_df)
    
    return results_df

def visualize_scalability_results(results_df):
    """Create visualizations for scalability test results
    
    Args:
        results_df: DataFrame with test results
    """
    protocols = results_df['Protocol'].unique()
    
    # Network lifetime vs network size
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Network Size'], protocol_data['Network Lifetime'], 
                marker='o', label=protocol)
    
    plt.title('Network Lifetime vs. Network Size')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Network Lifetime (time units)')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/scalability_tests/network_lifetime_vs_size.png")
    
    # Energy per node vs network size
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Network Size'], protocol_data['Energy Per Node'], 
                marker='o', label=protocol)
    
    plt.title('Energy Consumption Per Node vs. Network Size')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Energy Per Node')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/scalability_tests/energy_per_node_vs_size.png")
    
    # Packets per node vs network size
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Network Size'], protocol_data['Packets Per Node'], 
                marker='o', label=protocol)
    
    plt.title('Packets Delivered Per Node vs. Network Size')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Packets Per Node')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/scalability_tests/packets_per_node_vs_size.png")

if __name__ == "__main__":
    from config.simulation_config import get_config
    
    # Get base configuration
    config = get_config('medium')
    
    # Define network sizes to test
    network_sizes = [20, 50, 100, 200, 300]
    
    # Run scalability test
    results = test_scalability(config, network_sizes)
    
    print("Scalability test completed.")
    print("Results saved to output/scalability_tests/ directory.")