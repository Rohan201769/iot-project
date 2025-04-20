import os
from core.simulation import WSNSimulation
from utils.metrics import MetricsAnalyzer
from utils.visualization import WSNVisualizer

def compare_protocols(config, protocols=None):
    """Run simulations comparing different protocols
    
    Args:
        config: Base configuration dictionary
        protocols: List of protocol names to compare, or None for all
        
    Returns:
        MetricsAnalyzer: Analyzer with metrics for all protocols
    """
    if protocols is None:
        protocols = ["LEACH", "DirectedDiffusion", "GEAR", "PEGASIS"]
    
    analyzer = MetricsAnalyzer()
    visualizer = WSNVisualizer()
    
    # Ensure output directories exist
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/data", exist_ok=True)
    
    # Run simulations for each protocol
    for protocol_type in protocols:
        print(f"Simulating {protocol_type}...")
        sim_config = config.copy()
        sim_config['protocol_type'] = protocol_type
        
        # Create and run simulation
        simulation = WSNSimulation(sim_config)
        metrics = simulation.run()
        
        # Save metrics
        analyzer.add_protocol_metrics(protocol_type, metrics)
        
        # Visualize network topology
        visualizer.plot_network(simulation, save_path=f"output/images/{protocol_type}_topology.png")
    
    # Generate comparative visualizations
    # Generate comparative visualizations
    alive_nodes_data = analyzer.get_alive_nodes_data()
    energy_levels_data = analyzer.get_energy_levels_data()
    metrics_df = analyzer.get_metrics_dataframe()
    
    # Plot comparative results
    visualizer.plot_alive_nodes(alive_nodes_data, save_path="output/images/alive_nodes_comparison.png")
    visualizer.plot_energy_levels(energy_levels_data, save_path="output/images/energy_levels_comparison.png")
    visualizer.plot_comparison_bars(metrics_df, save_path="output/images/metrics_comparison.png")
    
    # Print summary
    analyzer.print_summary()
    
    # Save metrics data
    metrics_df.to_csv("output/data/protocol_comparison.csv", index=False)
    
    return analyzer

if __name__ == "__main__":
    # Define base configuration
    config = {
        'width': 100,
        'height': 100,
        'num_nodes': 100,
        'base_station_pos': (50, 50),
        'simulation_time': 1000,
        'packet_size': 4000,
        'comm_range': 30,
        'seed': 42  # Set seed for reproducibility
    }
    
    # Run comparison
    compare_protocols(config)