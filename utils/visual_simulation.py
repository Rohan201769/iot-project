import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
from matplotlib.patches import Circle, Arrow

class WSNVisualSimulation:
    """Real-time visualization for WSN simulation"""
    
    def __init__(self, simulation, interval=100, figsize=(10, 8)):
        """Initialize the visual simulation
        
        Args:
            simulation: WSNSimulation instance
            interval: Update interval in milliseconds
            figsize: Figure size (width, height) in inches
        """
        self.simulation = simulation
        self.interval = interval
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.transmission_events = []  # List of active transmissions to visualize
        self.event_duration = 5  # How long transmission events remain visible
        
        # Ensure output directory exists
        os.makedirs("output/animations", exist_ok=True)
        
        # For tracking simulation progress
        self.last_time = 0
        
    def start(self, save_animation=False):
        """Start the visual simulation
        
        Args:
            save_animation: Whether to save the animation as a file
        """
        # Initial setup
        self.setup_plot()
        
        # Create animation
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=self.interval,
            frames=int(self.simulation.simulation_time/10), blit=False)
        
        if save_animation:
            self.ani.save('output/animations/simulation.mp4', writer='ffmpeg', fps=15)
        
        plt.show()
        
    def setup_plot(self):
        """Set up the initial plot"""
        # Set plot limits
        self.ax.set_xlim(0, self.simulation.width)
        self.ax.set_ylim(0, self.simulation.height)
        
        # Add title and labels
        protocol_name = self.simulation.protocol.__class__.__name__
        self.ax.set_title(f'WSN Simulation - {protocol_name}')
        self.ax.set_xlabel('X coordinate')
        self.ax.set_ylabel('Y coordinate')
        
        # Add grid
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add color bar for energy levels
        self.energy_sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, 
                                              norm=plt.Normalize(vmin=0, vmax=1))
        self.energy_sm.set_array([])
        self.cbar = self.fig.colorbar(self.energy_sm, ax=self.ax, 
                                    label='Node Energy Level')
        
        # Add legend elements
        self.ax.plot([], [], 'ro', markersize=10, label='Base Station')
        self.ax.plot([], [], 'go', markersize=8, label='Cluster Head')
        self.ax.plot([], [], 'bo', markersize=6, label='Sensor Node')
        self.ax.plot([], [], 'ko', markersize=5, alpha=0.5, label='Dead Node')
        self.ax.plot([], [], 'y-', label='Transmission')
        self.ax.legend(loc='upper right')
        
        # Add stats text
        self.stats_text = self.ax.text(
            0.02, 0.02, '', transform=self.ax.transAxes,
            bbox=dict(facecolor='white', alpha=0.8))
        
        # Initialize node scatter plots
        self.node_scatter = self.ax.scatter([], [], s=[], c=[], 
                                         cmap=plt.cm.viridis, alpha=0.8)
        
        # Base station
        x, y = self.simulation.base_station.position
        self.bs_scatter = self.ax.scatter([x], [y], s=200, c='red', marker='s')
        
        # Transmission events (lines)
        self.transmission_lines = []
        
    def update(self, frame):
        """Update the visualization for each frame
        
        Args:
            frame: Frame number
        """
        # Progress the simulation if it's not already running
        time_now = frame * 10  # Convert frame to simulation time
        time_diff = time_now - self.last_time
        
        # Record any transmissions that happen during this frame
        self.record_transmissions(time_diff)
        
        # Update node positions and properties
        self.update_nodes()
        
        # Update transmission events
        self.update_transmissions()
        
        # Update stats text
        self.update_stats(time_now)
        
        self.last_time = time_now
        
        # Return all artists that need to be redrawn
        return [self.node_scatter, self.bs_scatter, self.stats_text]
    
    def record_transmissions(self, time_diff):
        """Record transmissions for visualization
        
        This would be hooked into the actual simulation in a real implementation
        For this demo, we'll simulate some random transmissions
        
        Args:
            time_diff: Time difference since last update
        """
        # In a real implementation, this would be linked to actual transmission events
        # For now, we'll generate some random transmissions
        if len(self.simulation.nodes) > 0:
            for _ in range(np.random.poisson(time_diff * 0.2)):  # Random number of events
                from_idx = np.random.randint(0, len(self.simulation.nodes))
                from_node = self.simulation.nodes[from_idx]
                
                if np.random.random() < 0.3:  # 30% chance to transmit to base station
                    to_node = self.simulation.base_station
                else:
                    to_idx = np.random.randint(0, len(self.simulation.nodes))
                    to_node = self.simulation.nodes[to_idx]
                
                # Only add transmissions from alive nodes
                if from_node.alive:
                    self.transmission_events.append({
                        'from': from_node,
                        'to': to_node,
                        'time': self.last_time,
                        'duration': self.event_duration,
                        'color': 'yellow' if isinstance(to_node, type(self.simulation.base_station)) 
                                else 'cyan'
                    })
    
    def update_nodes(self):
        """Update node positions and properties"""
        # Extract node data
        x, y, sizes, colors, alive = [], [], [], [], []
        
        for node in self.simulation.nodes:
            x.append(node.position[0])
            y.append(node.position[1])
            
            if node.alive:
                sizes.append(80 if node.is_cluster_head else 50)
                colors.append(node.energy)  # Will be mapped to color by the colormap
                alive.append(True)
            else:
                sizes.append(30)
                colors.append(0)
                alive.append(False)
        
        # Update scatter plot
        self.node_scatter.set_offsets(np.column_stack([x, y]))
        self.node_scatter.set_sizes(sizes)
        self.node_scatter.set_array(np.array(colors))
        
        # Update the color of nodes based on cluster head status
        face_colors = []
        for i, node in enumerate(self.simulation.nodes):
            if not node.alive:
                face_colors.append('gray')
            elif node.is_cluster_head:
                face_colors.append('green')
            else:
                face_colors.append(plt.cm.viridis(node.energy))
        
        self.node_scatter.set_facecolor(face_colors)
        
    def update_transmissions(self):
        """Update transmission visualizations"""
        # Clear old transmission lines
        for line in self.ax.lines:
            line.remove()
        
        # Draw active transmission events
        current_time = self.last_time
        active_events = []
        
        for event in self.transmission_events:
            if current_time - event['time'] < event['duration']:
                from_x, from_y = event['from'].position
                to_x, to_y = event['to'].position
                
                # Draw transmission line
                line = self.ax.plot([from_x, to_x], [from_y, to_y], 
                                   color=event['color'], alpha=0.7,
                                   linewidth=1.5, zorder=1)[0]
                
                active_events.append(event)
        
        # Keep only active events
        self.transmission_events = active_events
        
    def update_stats(self, time_now):
        """Update statistics text"""
        alive_count = sum(1 for node in self.simulation.nodes if node.alive)
        ch_count = sum(1 for node in self.simulation.nodes 
                      if node.alive and node.is_cluster_head)
        
        avg_energy = sum(node.energy for node in self.simulation.nodes) / len(self.simulation.nodes)
        
        stats = (f"Time: {time_now:.1f}\n"
                f"Alive Nodes: {alive_count}/{len(self.simulation.nodes)}\n"
                f"Cluster Heads: {ch_count}\n"
                f"Avg Energy: {avg_energy:.2f}\n"
                f"Packets: {self.simulation.base_station.packets_received}")
        
        self.stats_text.set_text(stats)