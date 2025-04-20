import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

class SimpleWSNVisualizer:
    """Simplified real-time visualization for WSN simulation"""
    
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
        
        # Ensure output directory exists
        os.makedirs("output/animations", exist_ok=True)
        
        # For tracking simulation progress
        self.frame_count = 0
        self.frames_total = int(simulation.simulation_time / 10)
        self.protocol_name = simulation.protocol.__class__.__name__
        
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
            frames=self.frames_total, blit=False, repeat=False)
        
        if save_animation:
            print(f"Saving animation to output/animations/{self.protocol_name}_simulation.mp4...")
            self.ani.save(f'output/animations/{self.protocol_name}_simulation.mp4', 
                         writer='ffmpeg', fps=15, dpi=100)
        
        plt.tight_layout()
        plt.show()
        
    def setup_plot(self):
        """Set up the initial plot"""
        # Set plot limits
        self.ax.set_xlim(0, self.simulation.width)
        self.ax.set_ylim(0, self.simulation.height)
        
        # Add title and labels
        self.ax.set_title(f'WSN Simulation - {self.protocol_name}')
        self.ax.set_xlabel('X coordinate')
        self.ax.set_ylabel('Y coordinate')
        
        # Add grid
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend elements
        self.ax.plot([], [], 'rs', markersize=10, label='Base Station')
        self.ax.plot([], [], 'go', markersize=8, label='Cluster Head')
        self.ax.plot([], [], 'bo', markersize=6, label='Regular Node')
        self.ax.plot([], [], 'ko', markersize=4, alpha=0.5, label='Dead Node')
        self.ax.legend(loc='upper right')
        
        # Add stats text and progress bar
        self.stats_text = self.ax.text(
            0.02, 0.02, '', transform=self.ax.transAxes,
            bbox=dict(facecolor='white', alpha=0.8))
        
        self.progress_text = self.ax.text(
            0.5, 0.02, '', transform=self.ax.transAxes, ha='center',
            bbox=dict(facecolor='lightblue', alpha=0.8))
        
        # Draw base station
        x, y = self.simulation.base_station.position
        self.bs = self.ax.scatter([x], [y], s=150, c='red', marker='s')
        
        # Initialize empty node plots
        self.ch_nodes = self.ax.scatter([], [], s=80, c='green')
        self.alive_nodes = self.ax.scatter([], [], s=50, c='blue')
        self.dead_nodes = self.ax.scatter([], [], s=30, c='gray', alpha=0.5)
        
    def update(self, frame):
        """Update the visualization for each frame
        
        Args:
            frame: Frame number
        """
        # Update simulation time
        self.frame_count = frame
        current_time = frame * 10  # Convert frame to simulation time
        
        # Collect node positions by type
        ch_x, ch_y = [], []
        alive_x, alive_y = [], []
        dead_x, dead_y = [], []
        
        for node in self.simulation.nodes:
            x, y = node.position
            
            if not node.alive:
                dead_x.append(x)
                dead_y.append(y)
            elif node.is_cluster_head:
                ch_x.append(x)
                ch_y.append(y)
            else:
                alive_x.append(x)
                alive_y.append(y)
        
        # Update scatter plots
        self.ch_nodes.set_offsets(np.column_stack([ch_x, ch_y]) if ch_x else np.empty((0, 2)))
        self.alive_nodes.set_offsets(np.column_stack([alive_x, alive_y]) if alive_x else np.empty((0, 2)))
        self.dead_nodes.set_offsets(np.column_stack([dead_x, dead_y]) if dead_x else np.empty((0, 2)))
        
        # Update statistics text
        alive_count = sum(1 for node in self.simulation.nodes if node.alive)
        ch_count = sum(1 for node in self.simulation.nodes if node.alive and node.is_cluster_head)
        avg_energy = sum(node.energy for node in self.simulation.nodes) / len(self.simulation.nodes)
        
        stats = (f"Time: {current_time}\n"
                f"Alive: {alive_count}/{len(self.simulation.nodes)}\n"
                f"Cluster Heads: {ch_count}\n"
                f"Avg Energy: {avg_energy:.2f}\n"
                f"Packets: {self.simulation.base_station.packets_received}")
        
        self.stats_text.set_text(stats)
        
        # Update progress
        progress_pct = (frame + 1) / self.frames_total * 100
        self.progress_text.set_text(f"Simulation Progress: {progress_pct:.1f}%")
        
        # Return all artists that need to be redrawn
        return [self.ch_nodes, self.alive_nodes, self.dead_nodes, 
                self.stats_text, self.progress_text]