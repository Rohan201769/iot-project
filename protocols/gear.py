import random
import numpy as np
from protocols.base_protocol import RoutingProtocol

class GEAR(RoutingProtocol):
    """Implementation of Geographic and Energy Aware Routing protocol"""
    
    def __init__(self, simulation, interest_interval=200):
        """Initialize GEAR protocol
        
        Args:
            simulation: WSNSimulation instance
            interest_interval: Interval for interest propagation
        """
        super().__init__(simulation)
        self.interest_interval = interest_interval
        self.target_regions = []  # list of (center_x, center_y, radius)
        self.routes = {}  # node -> next_hop
        
    def setup(self):
        """Setup GEAR protocol"""
        # Define target regions (could be dynamic in a real implementation)
        self.target_regions = [
            (self.simulation.width * 0.75, self.simulation.height * 0.75, 15),
            (self.simulation.width * 0.25, self.simulation.height * 0.25, 15)
        ]
        
    def run(self):
        """Execute GEAR protocol"""
        # Main protocol loop
        while True:
            # Propagate interest to target regions
            if self.env.now % self.interest_interval == 0:
                yield self.env.process(self.propagate_interest())
            
            # Detect events and send data
            yield self.env.process(self.detect_and_forward())
            
            yield self.env.timeout(10)
    
    def propagate_interest(self):
        """Propagate interest from base station to target regions"""
        for target_region in self.target_regions:
            center_x, center_y, radius = target_region
            
            # Geographic forwarding to the target region
            for node in self.nodes:
                if not node.alive:
                    continue
                    
                # Check if node is in target region
                node_distance_to_region = np.sqrt((node.position[0] - center_x)**2 + 
                                               (node.position[1] - center_y)**2)
                
                if node_distance_to_region <= radius:
                    # Discover route from base station to this node
                    route = self.discover_route(self.base_station.position, node)
                    
                    # Store reverse route for data delivery
                    if route:
                        current = node
                        for next_hop in reversed(route[:-1]):  # skip base station
                            if next_hop in self.nodes:
                                self.routes[current] = next_hop
                                current = next_hop
        
        yield self.env.timeout(20)
    
    def discover_route(self, start_pos, target_node):
        """GEAR route discovery from start position to target node
        
        Args:
            start_pos: (x, y) position to start from
            target_node: Target node object
            
        Returns:
            list: Route as a list of nodes, or None if no route found
        """
        # Start from nodes closest to the start position
        queue = []
        visited = set()
        prev = {}  # node -> previous_node
        
        # Find closest node to start position
        min_distance = float('inf')
        start_node = None
        
        for node in self.nodes:
            if node.alive:
                distance = np.sqrt((node.position[0] - start_pos[0])**2 + 
                                 (node.position[1] - start_pos[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    start_node = node
        
        if not start_node:
            return None
            
        queue.append(start_node)
        visited.add(start_node.id)
        
        # BFS with geographic and energy considerations
        while queue:
            current = queue.pop(0)
            
            if current.id == target_node.id:
                # Found target, reconstruct path
                path = [current]
                while current.id != start_node.id:
                    current = prev[current]
                    path.append(current)
                
                path.reverse()
                return path
            
            # Get neighbors sorted by cost function
            neighbors = []
            for neighbor in current.neighbors:
                if neighbor.alive and neighbor.id not in visited:
                    # Calculate geographic progress
                    current_distance = np.sqrt((current.position[0] - target_node.position[0])**2 + 
                                            (current.position[1] - target_node.position[1])**2)
                    neighbor_distance = np.sqrt((neighbor.position[0] - target_node.position[0])**2 + 
                                             (neighbor.position[1] - target_node.position[1])**2)
                    progress = current_distance - neighbor_distance
                    
                    # Energy factor
                    energy_factor = neighbor.energy
                    
                    # Combined cost (higher is better)
                    cost = progress * energy_factor
                    
                    neighbors.append((neighbor, cost))
            
            # Sort neighbors by cost (higher cost first)
            neighbors.sort(key=lambda x: x[1], reverse=True)
            
            # Add neighbors to queue
            for neighbor, _ in neighbors:
                queue.append(neighbor)
                visited.add(neighbor.id)
                prev[neighbor] = current
                
                # Simulate energy consumption for route discovery
                distance = current.distance_to(neighbor)
                current.transmit(50, distance)
                neighbor.receive(50)
        
        return None  # No path found
    
    def detect_and_forward(self):
        """Detect events in target regions and forward data"""
        for target_region in self.target_regions:
            center_x, center_y, radius = target_region
            
            # Check for events in target region
            for node in self.nodes:
                if not node.alive:
                    continue
                
                # Check if node is in target region
                node_distance_to_region = np.sqrt((node.position[0] - center_x)**2 + 
                                               (node.position[1] - center_y)**2)
                
                if node_distance_to_region <= radius and random.random() < 0.05:
                    # Node detects an event
                    node.sense(self.packet_size)
                    
                    # Forward data using stored routes
                    current = node
                    data_size = self.packet_size
                    
                    while current in self.routes:
                        next_hop = self.routes[current]
                        
                        if not next_hop.alive:
                            # Update route if next hop is dead
                            route = self.discover_route(current.position, self.base_station.position)
                            if route and len(route) > 1:
                                self.routes[current] = route[1]
                                next_hop = route[1]
                            else:
                                break
                        
                        # Transmit data
                        distance = current.distance_to(next_hop)
                        if not current.transmit(data_size, distance):
                            break
                            
                        if not next_hop.receive(data_size):
                            break
                        
                        current = next_hop
                        
                        # Check if we reached a node close to the base station
                        bs_distance = next_hop.distance_to(self.base_station)
                        if bs_distance <= 20:
                            # Deliver to base station
                            if next_hop.transmit(data_size, bs_distance):
                                self.base_station.receive_data(data_size)
                            break
        
        yield self.env.timeout(10)