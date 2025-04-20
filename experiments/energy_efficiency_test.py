"""
Energy Efficiency Test
---------------------

This script tests energy efficiency of protocols under different scenarios.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from core.simulation import WSNSimulation
from utils.metrics import MetricsAnalyzer
from utils.visualization import WSNVisualizer

def test_energy_efficiency(base_config, packet_sizes, protocols=None):
    """Test energy efficiency with varying packet sizes
    
    Args:
        base_config: Base configuration dictionary
        packet_sizes: List of packet sizes to test
        protocols: List of protocol names to test
        
    Returns:
        pd.DataFrame: Results for all tests
    """
    if protocols is None:
        protocols = ["LEACH", "DirectedDiffusion", "GEAR", "PEGASIS"]
    
    # Ensure output directories exist
    os.makedirs("output/energy_tests", exist_ok=True)
    
    results = []
    
    for protocol in protocols:
        for packet_size in packet_sizes:
            print(f"Testing {protocol} with packet size {packet_size}...")
            
            # Configure simulation
            config = base_config.copy()
            config['protocol_type'] = protocol
            config['packet_size'] = packet_size
            
            # Run simulation
            simulation = WSNSimulation(config)
            metrics = simulation.run()
            
            # Record results
            energy_efficiency = metrics['packets_delivered'] / (metrics['total_energy_consumed'] + 0.001)
            results.append({
                'Protocol': protocol,
                'Packet Size': packet_size,
                'Energy Efficiency': energy_efficiency,
                'Network Lifetime': metrics['network_lifetime'],
                'Packets Delivered': metrics['packets_delivered'],
                'Total Energy Consumed': metrics['total_energy_consumed']
            })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv("output/energy_tests/energy_efficiency_results.csv", index=False)
    
    # Create visualizations
    visualize_energy_efficiency_results(results_df)
    
    return results_df

def visualize_energy_efficiency_results(results_df):
    """Create visualizations for energy efficiency test results
    
    Args:
        results_df: DataFrame with test results
    """
    protocols = results_df['Protocol'].unique()
    packet_sizes = results_df['Packet Size'].unique()
    
    # Energy efficiency vs packet size for each protocol
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Packet Size'], protocol_data['Energy Efficiency'], 
                marker='o', label=protocol)
    
    plt.title('Energy Efficiency vs. Packet Size')
    plt.xlabel('Packet Size (bits)')
    plt.ylabel('Energy Efficiency (packets/energy unit)')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/energy_tests/energy_efficiency_vs_packet_size.png")
    
    # Network lifetime vs packet size
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Packet Size'], protocol_data['Network Lifetime'], 
                marker='o', label=protocol)
    
    plt.title('Network Lifetime vs. Packet Size')
    plt.xlabel('Packet Size (bits)')
    plt.ylabel('Network Lifetime (time units)')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/energy_tests/network_lifetime_vs_packet_size.png")
    
    # Packets delivered vs packet size
    plt.figure(figsize=(12, 8))
    for protocol in protocols:
        protocol_data = results_df[results_df['Protocol'] == protocol]
        plt.plot(protocol_data['Packet Size'], protocol_data['Packets Delivered'], 
                marker='o', label=protocol)
    
    plt.title('Packets Delivered vs. Packet Size')
    plt.xlabel('Packet Size (bits)')
    plt.ylabel('Packets Delivered')
    plt.grid(True)
    plt.legend()
    plt.savefig("output/energy_tests/packets_delivered_vs_packet_size.png")

if __name__ == "__main__":
    from config.simulation_config import get_config
    
    # Get base configuration
    config = get_config('medium')
    
    # Define packet sizes to test
    # Define packet sizes to test
    packet_sizes = [1000, 2000, 4000, 8000, 16000]
    
    # Run energy efficiency test
    results = test_energy_efficiency(config, packet_sizes)
    
    print("Energy efficiency test completed.")
    print("Results saved to output/energy_tests/ directory.")