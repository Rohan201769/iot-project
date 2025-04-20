import pandas as pd
import numpy as np

class MetricsAnalyzer:
    """Class for analyzing and comparing protocol metrics"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.protocol_metrics = {}
        
    def add_protocol_metrics(self, protocol_name, metrics):
        """Add metrics for a protocol
        
        Args:
            protocol_name: Name of the protocol
            metrics: Dictionary of metrics
        """
        self.protocol_metrics[protocol_name] = metrics
        
    def get_metrics_dataframe(self):
        """Create a DataFrame with all protocol metrics
        
        Returns:
            pd.DataFrame: DataFrame with comparative metrics
        """
        data = []
        for protocol, metrics in self.protocol_metrics.items():
            row = {
                'Protocol': protocol,
                'Network Lifetime': metrics.get('network_lifetime', 0),
                'Packets Delivered': metrics.get('packets_delivered', 0),
                'Energy Efficiency': metrics.get('packets_delivered', 0) / 
                                     (metrics.get('total_energy_consumed', 1) + 0.001),
                'Total Energy Consumed': metrics.get('total_energy_consumed', 0)
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_alive_nodes_data(self):
        """Get data for alive nodes over time for all protocols
        
        Returns:
            dict: Protocol name -> (time_points, alive_nodes)
        """
        result = {}
        for protocol, metrics in self.protocol_metrics.items():
            time_points = metrics.get('time_points', [])
            alive_nodes = metrics.get('alive_nodes', [])
            result[protocol] = (time_points, alive_nodes)
        
        return result
    
    def get_energy_levels_data(self):
        """Get data for energy levels over time for all protocols
        
        Returns:
            dict: Protocol name -> (time_points, energy_levels)
        """
        result = {}
        for protocol, metrics in self.protocol_metrics.items():
            time_points = metrics.get('time_points', [])
            energy_levels = metrics.get('energy_levels', [])
            result[protocol] = (time_points, energy_levels)
        
        return result
    
    def print_summary(self):
        """Print a summary of all protocol metrics"""
        df = self.get_metrics_dataframe()
        print("Protocol Performance Summary:")
        print("-----------------------------")
        for _, row in df.iterrows():
            protocol = row['Protocol']
            print(f"\n{protocol}:")
            print(f"  Network Lifetime: {row['Network Lifetime']:.2f} time units")
            print(f"  Packets Delivered: {row['Packets Delivered']}")
            print(f"  Energy Efficiency: {row['Energy Efficiency']:.4f} packets/energy unit")
            print(f"  Total Energy Consumed: {row['Total Energy Consumed']:.4f} energy units")
            
        # Identify best protocol for each metric
        best_lifetime = df.loc[df['Network Lifetime'].idxmax()]
        best_packets = df.loc[df['Packets Delivered'].idxmax()]
        best_efficiency = df.loc[df['Energy Efficiency'].idxmax()]
        least_energy = df.loc[df['Total Energy Consumed'].idxmin()]
        
        print("\nBest Protocols:")
        print(f"  Network Lifetime: {best_lifetime['Protocol']} ({best_lifetime['Network Lifetime']:.2f} time units)")
        print(f"  Packets Delivered: {best_packets['Protocol']} ({best_packets['Packets Delivered']} packets)")
        print(f"  Energy Efficiency: {best_efficiency['Protocol']} ({best_efficiency['Energy Efficiency']:.4f} packets/energy unit)")
        print(f"  Energy Conservation: {least_energy['Protocol']} ({least_energy['Total Energy Consumed']:.4f} energy units)")