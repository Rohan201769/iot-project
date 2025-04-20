import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

class WSNVisualizer:
    """Class for visualizing WSN simulation results"""
    
    def __init__(self, figsize=(12, 8)):
        """Initialize the visualizer
        
        Args:
            figsize: Figure size for plots
        """
        self.figsize = figsize
        self.colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink', 'gray']
        
    def plot_network(self, simulation, save_path=None):
        """Plot the network topology
        
        Args:
            simulation: WSNSimulation instance
            save_path: Path to save the figure, or None for display
        """
        plt.figure(figsize=self.figsize)
        
        # Create a graph
        G = nx.Graph()
        
        # Add nodes
        for node in simulation.nodes:
            G.add_node(node.id, pos=node.position, alive=node.alive, 
                      is_ch=node.is_cluster_head, energy=node.energy)
            
            # Add edges for neighbors
            for neighbor in node.neighbors:
                if neighbor.id > node.id:  # Add each edge only once
                    G.add_edge(node.id, neighbor.id)
        
        # Get node positions for drawing
        pos = nx.get_node_attributes(G, 'pos')
        
        # Get node colors based on role and energy
        colors = []
        sizes = []
        for node_id in G.nodes():
            if node_id == simulation.base_station.id:
                colors.append('red')
                sizes.append(300)
            elif G.nodes[node_id]['is_ch']:
                colors.append('green')
                sizes.append(200)
            elif G.nodes[node_id]['alive']:
                energy = G.nodes[node_id]['energy']
                # Color gradient from yellow (low energy) to blue (high energy)
                colors.append((1-energy, 1-energy, energy))
                sizes.append(100)
            else:
                colors.append('gray')
                sizes.append(50)
        
        # Draw the graph
        nx.draw(G, pos, node_color=colors, node_size=sizes, 
               with_labels=True, font_size=8, alpha=0.8)
        
        # Add base station
        plt.plot(simulation.base_station.position[0], simulation.base_station.position[1], 
                'rs', markersize=15, label='Base Station')
        
        # Add legend
        plt.legend(loc='upper right')
        
        plt.title(f'Network Topology - {simulation.protocol.get_name()}')
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def plot_alive_nodes(self, metrics_data, save_path=None):
        """Plot alive nodes over time for multiple protocols
        
        Args:
            metrics_data: Dict of protocol name -> (time_points, alive_nodes)
            save_path: Path to save the figure, or None for display
        """
        plt.figure(figsize=self.figsize)
        
        for i, (protocol, (time_points, alive_nodes)) in enumerate(metrics_data.items()):
            plt.plot(time_points, alive_nodes, 
                    color=self.colors[i % len(self.colors)], 
                    marker='o', markersize=3, label=protocol)
        
        plt.title('Number of Alive Nodes over Time')
        plt.xlabel('Simulation Time')
        plt.ylabel('Number of Alive Nodes')
        plt.grid(True)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def plot_energy_levels(self, metrics_data, save_path=None):
        """Plot energy levels over time for multiple protocols
        
        Args:
            metrics_data: Dict of protocol name -> (time_points, energy_levels)
            save_path: Path to save the figure, or None for display
        """
        plt.figure(figsize=self.figsize)
        
        for i, (protocol, (time_points, energy_levels)) in enumerate(metrics_data.items()):
            plt.plot(time_points, energy_levels, 
                    color=self.colors[i % len(self.colors)], 
                    marker='o', markersize=3, label=protocol)
        
        plt.title('Average Energy Level over Time')
        plt.xlabel('Simulation Time')
        plt.ylabel('Average Energy Level')
        plt.grid(True)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def plot_comparison_bars(self, metrics_df, save_path=None):
        """Plot bar charts comparing protocol performance metrics
        
        Args:
            metrics_df: DataFrame with protocol metrics
            save_path: Path to save the figure, or None for display
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        
        # Network Lifetime
        metrics_df.plot(x='Protocol', y='Network Lifetime', kind='bar', 
                       ax=axes[0, 0], color='blue', legend=False)
        axes[0, 0].set_title('Network Lifetime')
        axes[0, 0].set_ylabel('Time Units')
        
        # Packets Delivered
        metrics_df.plot(x='Protocol', y='Packets Delivered', kind='bar', 
                       ax=axes[0, 1], color='green', legend=False)
        axes[0, 1].set_title('Packets Delivered')
        axes[0, 1].set_ylabel('Packets')
        
        # Energy Efficiency
        metrics_df.plot(x='Protocol', y='Energy Efficiency', kind='bar', 
                       ax=axes[1, 0], color='orange', legend=False)
        axes[1, 0].set_title('Energy Efficiency')
        axes[1, 0].set_ylabel('Packets/Energy Unit')
        
        # Total Energy Consumed
        metrics_df.plot(x='Protocol', y='Total Energy Consumed', kind='bar', 
                       ax=axes[1, 1], color='red', legend=False)
        axes[1, 1].set_title('Total Energy Consumed')
        axes[1, 1].set_ylabel('Energy Units')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()