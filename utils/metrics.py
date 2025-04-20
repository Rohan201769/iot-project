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
            # Add the new lifetime metrics
            print(f"  Time to First Node Death: {self.protocol_metrics[protocol].get('first_dead_time', 0):.2f} time units")
            print(f"  Time to Half Network Death: {self.protocol_metrics[protocol].get('half_dead_time', 0):.2f} time units")
            # Keep existing metrics
            print(f"  Network Lifetime: {row['Network Lifetime']:.2f} time units")
            print(f"  Packets Delivered: {row['Packets Delivered']}")
            print(f"  Energy Efficiency: {row['Energy Efficiency']:.4f} packets/energy unit")
            print(f"  Total Energy Consumed: {row['Total Energy Consumed']:.4f} energy units")
            
        # Identify best protocol for each metric - keep your existing code
        best_lifetime = df.loc[df['Network Lifetime'].idxmax()]
        best_packets = df.loc[df['Packets Delivered'].idxmax()]
        best_efficiency = df.loc[df['Energy Efficiency'].idxmax()]
        least_energy = df.loc[df['Total Energy Consumed'].idxmin()]
        
        # Add new "best" categories for the new metrics
        first_dead_times = {p: self.protocol_metrics[p].get('first_dead_time', 0) for p in self.protocol_metrics}
        if any(first_dead_times.values()):  # Only if we have some non-zero values
            best_first_dead = max(first_dead_times.items(), key=lambda x: x[1] if x[1] > 0 else 0)
        else:
            best_first_dead = (next(iter(first_dead_times.keys())), 0)

        half_dead_times = {p: self.protocol_metrics[p].get('half_dead_time', 0) for p in self.protocol_metrics}
        if any(half_dead_times.values()):  # Only if we have some non-zero values
            best_half_dead = max(half_dead_times.items(), key=lambda x: x[1] if x[1] > 0 else 0)
        else:
            best_half_dead = (next(iter(half_dead_times.keys())), 0)
        
        print("\nBest Protocols:")
        if best_first_dead[1] > 0:
            print(f"  Time to First Node Death: {best_first_dead[0]} ({best_first_dead[1]:.2f} time units)")
        if best_half_dead[1] > 0:
            print(f"  Time to Half Network Death: {best_half_dead[0]} ({best_half_dead[1]:.2f} time units)")
        
        # Keep your existing "best" outputs
        print(f"  Network Lifetime: {best_lifetime['Protocol']} ({best_lifetime['Network Lifetime']:.2f} time units)")
        print(f"  Packets Delivered: {best_packets['Protocol']} ({best_packets['Packets Delivered']} packets)")
        print(f"  Energy Efficiency: {best_efficiency['Protocol']} ({best_efficiency['Energy Efficiency']:.4f} packets/energy unit)")
        print(f"  Energy Conservation: {least_energy['Protocol']} ({least_energy['Total Energy Consumed']:.4f} energy units)")