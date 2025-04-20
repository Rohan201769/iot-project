import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import random
from matplotlib.patches import Circle

class SimpleWSNVisualizer:
    """Enhanced real-time visualization for WSN simulation"""
    
    def __init__(self, simulation, interval=100, figsize=(12, 9)):
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
        
        # For tracking simulation progress and visualizing events
        self.frame_count = 0
        self.frames_total = int(simulation.simulation_time / 10)
        self.protocol_name = simulation.protocol.__class__.__name__
        
        # Transmission events
        self.transmission_events = []
        self.transmission_duration = 10  # How many frames a transmission remains visible
        
        # Cluster visualization (for LEACH)
        self.clusters = {}  # CH -> member nodes
        self.cluster_patches = []
        
        # Chain visualization (for PEGASIS)
        self.chain = []
        self.chain_line = None
        
        # Interest propagation (for Directed Diffusion)
        self.interests = []
        self.interest_lines = []
        
        # Target regions (for GEAR)
        self.target_regions = []
        self.region_patches = []
        
        # Last energy values to detect changes
        self.last_energies = [node.energy for node in simulation.nodes]
        
        # Initialize protocol-specific visual elements
        self._init_protocol_visuals()
        
    def _init_protocol_visuals(self):
        """Initialize protocol-specific visualization elements"""
        if self.protocol_name == 'LEACH':
            # Nothing special to initialize for LEACH
            pass
            
        elif self.protocol_name == 'PEGASIS':
            # Initialize chain if available
            if hasattr(self.simulation.protocol, 'chain'):
                self.chain = self.simulation.protocol.chain
                
        elif self.protocol_name == 'DirectedDiffusion':
            # Nothing special to initialize for Directed Diffusion
            pass
            
        elif self.protocol_name == 'GEAR':
            # Initialize target regions if available
            if hasattr(self.simulation.protocol, 'target_regions'):
                self.target_regions = self.simulation.protocol.target_regions
                
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
        self.ax.set_title(f'WSN Simulation - {self.protocol_name}', fontsize=14)
        self.ax.set_xlabel('X coordinate')
        self.ax.set_ylabel('Y coordinate')
        
        # Add grid
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend elements
        self.ax.plot([], [], 'rs', markersize=10, label='Base Station')
        self.ax.plot([], [], 'go', markersize=8, label='Cluster Head')
        self.ax.plot([], [], 'bo', markersize=6, label='Regular Node')
        self.ax.plot([], [], 'ko', markersize=4, alpha=0.5, label='Dead Node')
        self.ax.plot([], [], 'y-', linewidth=1.5, label='Transmission')
        
        # Add protocol-specific legend items
        if self.protocol_name == 'LEACH':
            self.ax.plot([], [], 'g--', alpha=0.3, label='Cluster Boundary')
        elif self.protocol_name == 'PEGASIS':
            self.ax.plot([], [], 'c-', linewidth=2, label='Chain')
        elif self.protocol_name == 'DirectedDiffusion':
            self.ax.plot([], [], 'm-->', alpha=0.6, label='Interest Propagation')
        elif self.protocol_name == 'GEAR':
            self.ax.fill([], [], 'r', alpha=0.1, label='Target Region')
            
        self.ax.legend(loc='upper right')
        
        # Add stats text and progress bar
        self.stats_text = self.ax.text(
            0.02, 0.02, '', transform=self.ax.transAxes,
            bbox=dict(facecolor='white', alpha=0.8), fontsize=10)
        
        self.protocol_text = self.ax.text(
            0.02, 0.97, f'Protocol: {self.protocol_name}', 
            transform=self.ax.transAxes, ha='left', va='top',
            bbox=dict(facecolor='lightyellow', alpha=0.8), fontsize=12)
        
        self.progress_text = self.ax.text(
            0.5, 0.02, '', transform=self.ax.transAxes, ha='center',
            bbox=dict(facecolor='lightblue', alpha=0.8), fontsize=10)
        
        # Draw base station
        x, y = self.simulation.base_station.position
        self.bs = self.ax.scatter([x], [y], s=150, c='red', marker='s')
        
        # Initialize empty node plots
        self.ch_nodes = self.ax.scatter([], [], s=80, c='green')
        self.alive_nodes = self.ax.scatter([], [], s=50, c='blue')
        self.dead_nodes = self.ax.scatter([], [], s=30, c='gray', alpha=0.5)
        
        # Initialize protocol-specific visual elements
        if self.protocol_name == 'GEAR' and self.target_regions:
            for center_x, center_y, radius in self.target_regions:
                circle = plt.Circle((center_x, center_y), radius, 
                                   color='red', fill=True, alpha=0.1)
                self.ax.add_patch(circle)
                self.region_patches.append(circle)
                
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
        
        # Update protocol-specific visualizations
        if self.protocol_name == 'LEACH':
            self._update_leach_visualization()
        elif self.protocol_name == 'PEGASIS':
            self._update_pegasis_visualization()
        elif self.protocol_name == 'DirectedDiffusion':
            self._update_dd_visualization()
        elif self.protocol_name == 'GEAR':
            self._update_gear_visualization()
            
        # Generate simulated transmission events
        self._generate_transmissions()
        
        # Update transmissions
        self._update_transmissions()
        
        # Update statistics text
        alive_count = sum(1 for node in self.simulation.nodes if node.alive)
        ch_count = sum(1 for node in self.simulation.nodes if node.alive and node.is_cluster_head)
        avg_energy = sum(node.energy for node in self.simulation.nodes) / len(self.simulation.nodes)
        energy_consumed = len(self.simulation.nodes) - sum(node.energy for node in self.simulation.nodes)
        
        # Update energy changes
        energy_diffs = [prev - curr for prev, curr in 
                      zip(self.last_energies, [node.energy for node in self.simulation.nodes])]
        energy_changed = sum(1 for diff in energy_diffs if diff > 0.001)
        self.last_energies = [node.energy for node in self.simulation.nodes]
        
        stats = (f"Time: {current_time}\n"
                f"Alive Nodes: {alive_count}/{len(self.simulation.nodes)}\n"
                f"Cluster Heads: {ch_count}\n"
                f"Avg Energy: {avg_energy:.2f}\n"
                f"Energy Consumed: {energy_consumed:.2f}\n"
                f"Nodes Active: {energy_changed}\n"
                f"Packets Delivered: {self.simulation.base_station.packets_received}")
        
        self.stats_text.set_text(stats)
        
        # Update progress
        progress_pct = (frame + 1) / self.frames_total * 100
        self.progress_text.set_text(f"Simulation Progress: {progress_pct:.1f}%")
        
        return True
    
    def _update_leach_visualization(self):
        """Update LEACH-specific visualization elements"""
        # Clear old cluster visualizations
        for patch in self.cluster_patches:
            patch.remove()
        self.cluster_patches = []
        
        # Get current clusters
        if hasattr(self.simulation.protocol, 'clusters'):
            self.clusters = self.simulation.protocol.clusters
            
            # Draw cluster boundaries
            for ch, members in self.clusters.items():
                if not ch.alive or not members:
                    continue
                    
                # Calculate convex hull of cluster
                points = [ch.position] + [node.position for node in members if node.alive]
                if len(points) < 3:
                    continue
                    
                # Simplified approach: just draw a circle around the cluster
                x_avg = sum(p[0] for p in points) / len(points)
                y_avg = sum(p[1] for p in points) / len(points)
                radius = max(np.sqrt((p[0] - x_avg)**2 + (p[1] - y_avg)**2) for p in points)
                
                circle = plt.Circle((x_avg, y_avg), radius * 1.1, 
                                  color='green', fill=False, alpha=0.3, linestyle='--')
                self.ax.add_patch(circle)
                self.cluster_patches.append(circle)
    
    def _update_pegasis_visualization(self):
        """Update PEGASIS-specific visualization elements"""
        # Remove old chain line
        if self.chain_line:
            self.chain_line.remove()
            self.chain_line = None
            
        # Get current chain
        if hasattr(self.simulation.protocol, 'chain'):
            self.chain = self.simulation.protocol.chain
            
            if self.chain and len(self.chain) > 1:
                # Draw chain line connecting nodes in sequence
                chain_x = [node.position[0] for node in self.chain if node.alive]
                chain_y = [node.position[1] for node in self.chain if node.alive]
                
                if len(chain_x) > 1:
                    self.chain_line = self.ax.plot(chain_x, chain_y, 'c-', linewidth=2)[0]
    
    def _update_dd_visualization(self):
        """Update Directed Diffusion-specific visualization elements"""
        # Clear old interest lines
        for line in self.interest_lines:
            if line in self.ax.lines:
                line.remove()
        self.interest_lines = []
        
        # Simulate interest propagation
        if self.frame_count % 50 == 0:  # Periodically add new interests
            # Start interest from base station
            bs_x, bs_y = self.simulation.base_station.position
            
            # Pick 3 random nodes to propagate interest to
            targets = random.sample(self.simulation.nodes, 
                                  min(3, len(self.simulation.nodes)))
            
            for target in targets:
                if not target.alive:
                    continue
                    
                # Create interest line
                line = self.ax.plot([bs_x, target.position[0]], 
                                  [bs_y, target.position[1]], 
                                  'm--', alpha=0.6, marker='>')[0]
                self.interest_lines.append(line)
                
                # Add interest to remember
                self.interests.append({
                    'from': (bs_x, bs_y),
                    'to': target.position,
                    'time': self.frame_count,
                    'duration': 20  # interests visible for 20 frames
                })
                
        # Remove old interests
        self.interests = [interest for interest in self.interests 
                         if self.frame_count - interest['time'] < interest['duration']]
    
    def _update_gear_visualization(self):
        """Update GEAR-specific visualization elements"""
        # GEAR visualization is mainly handled in setup_plot with target regions
        pass
    
    def _generate_transmissions(self):
        """Generate simulated transmission events"""
        # Every few frames, generate new transmissions
        if self.frame_count % 5 == 0:
            # Generate node-to-CH or CH-to-BS transmissions based on protocol
            if self.protocol_name == 'LEACH':
                # In LEACH: nodes transmit to their cluster head
                for ch, members in self.clusters.items():
                    if not ch.alive:
                        continue
                        
                    # Some members transmit to CH
                    for node in random.sample(members, min(2, len(members))):
                        if node.alive and random.random() < 0.3:
                            self._add_transmission(node, ch)
                            
                    # CH may transmit to base station
                    if random.random() < 0.2:
                        self._add_transmission(ch, self.simulation.base_station)
                
            elif self.protocol_name == 'PEGASIS':
                # In PEGASIS: transmit along the chain towards the leader
                if self.chain and len(self.chain) > 1:
                    # Find leader
                    leader = None
                    if hasattr(self.simulation.protocol, 'leader'):
                        leader = self.simulation.protocol.leader
                    
                    if not leader and self.chain:
                        leader = self.chain[0]  # Fallback
                        
                    if leader and leader.alive:
                        # Transmit along chain towards leader
                        for i in range(1, min(3, len(self.chain))):
                            if random.random() < 0.3 and self.chain[i].alive:
                                self._add_transmission(self.chain[i], self.chain[i-1])
                                
                        # Leader transmits to base station
                        if random.random() < 0.2:
                            self._add_transmission(leader, self.simulation.base_station)
            
            elif self.protocol_name == 'DirectedDiffusion':
                # In DD: nodes with interests transmit along gradients
                alive_nodes = [node for node in self.simulation.nodes if node.alive]
                if not alive_nodes:
                    return
                    
                # Some nodes transmit directly to base station (gradient paths)
                for _ in range(min(3, len(alive_nodes))):
                    node = random.choice(alive_nodes)
                    if random.random() < 0.2:
                        self._add_transmission(node, self.simulation.base_station)
                
            elif self.protocol_name == 'GEAR':
                # In GEAR: nodes in target regions transmit towards base station through geographic routing
                for center_x, center_y, radius in self.target_regions:
                    # Find nodes in target region
                    nodes_in_region = []
                    for node in self.simulation.nodes:
                        if not node.alive:
                            continue
                            
                        dist = np.sqrt((node.position[0] - center_x)**2 + 
                                     (node.position[1] - center_y)**2)
                        if dist <= radius:
                            nodes_in_region.append(node)
                    
                    # Some nodes in region transmit data
                    for node in random.sample(nodes_in_region, 
                                           min(2, len(nodes_in_region))):
                        if random.random() < 0.3:
                            # Find a node closer to BS as next hop
                            bs_x, bs_y = self.simulation.base_station.position
                            node_dist_to_bs = np.sqrt((node.position[0] - bs_x)**2 + 
                                                   (node.position[1] - bs_y)**2)
                            
                            next_hop = None
                            for neighbor in self.simulation.nodes:
                                if not neighbor.alive or neighbor.id == node.id:
                                    continue
                                    
                                neighbor_dist = np.sqrt((neighbor.position[0] - bs_x)**2 + 
                                                     (neighbor.position[1] - bs_y)**2)
                                if (neighbor_dist < node_dist_to_bs and 
                                    np.sqrt((neighbor.position[0] - node.position[0])**2 + 
                                          (neighbor.position[1] - node.position[1])**2) < 30):
                                    next_hop = neighbor
                                    break
                            
                            if next_hop:
                                self._add_transmission(node, next_hop)
                            else:
                                # Direct to base station if no suitable next hop
                                self._add_transmission(node, self.simulation.base_station)
    
    def _add_transmission(self, from_node, to_node):
        """Add a transmission event"""
        self.transmission_events.append({
            'from': from_node.position if hasattr(from_node, 'position') else from_node,
            'to': to_node.position if hasattr(to_node, 'position') else to_node,
            'time': self.frame_count,
            'duration': self.transmission_duration,
            'color': 'yellow' if hasattr(to_node, 'packets_received') else 'cyan'
        })
    
    def _update_transmissions(self):
        """Update transmission visualizations"""
        # Clear old transmission lines
        for line in self.ax.lines[5:]:  # Skip the first 5 lines (legend items)
            line.remove()
        
        # Draw active transmission events
        active_events = []
        
        for event in self.transmission_events:
            if self.frame_count - event['time'] < event['duration']:
                from_x, from_y = event['from'] if isinstance(event['from'], tuple) else event['from']
                to_x, to_y = event['to'] if isinstance(event['to'], tuple) else event['to']
                
                # Draw transmission line
                self.ax.plot([from_x, to_x], [from_y, to_y], 
                           color=event['color'], alpha=0.7,
                           linewidth=1.5, zorder=5)
                
                active_events.append(event)
        
        # Keep only active events
        self.transmission_events = active_events