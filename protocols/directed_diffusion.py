import random
from protocols.base_protocol import RoutingProtocol

class DirectedDiffusion(RoutingProtocol):
    """Implementation of the Directed Diffusion protocol"""
    
    def __init__(self, simulation, interest_interval=200, reinforcement_interval=50):
        """Initialize Directed Diffusion protocol
        
        Args:
            simulation: WSNSimulation instance
            interest_interval: Interval for interest propagation
            reinforcement_interval: Interval for path reinforcement
        """
        super().__init__(simulation)
        self.interest_interval = interest_interval
        self.reinforcement_interval = reinforcement_interval
        self.gradients = {}  # node -> {neighbor: reinforcement}
        self.events_detected = {}  # node_id -> time of last event
        
    def setup(self):
        """Setup directed diffusion protocol"""
        # Initialize gradients
        for node in self.nodes:
            if node.alive:
                self.gradients[node] = {}
    
    def run(self):
        """Execute Directed Diffusion protocol"""
        # Initial interest propagation
        yield self.env.process(self.propagate_interest())
        
        # Main protocol loop
        while True:
            # Periodically detect events
            yield self.env.process(self.detect_events())
            
            # Data delivery along gradients
            yield self.env.process(self.deliver_data())
            
            # Periodically reinforce paths
            if self.env.now % self.reinforcement_interval == 0:
                yield self.env.process(self.reinforce_paths())
            
            # Periodically re-propagate interest
            if self.env.now % self.interest_interval == 0:
                yield self.env.process(self.propagate_interest())
            
            yield self.env.timeout(10)
    
    def propagate_interest(self):
        """Propagate interest from base station to all nodes"""
        # Initialize gradients
        for node in self.nodes:
            if node.alive:
                self.gradients[node] = {}
        
        # Queue for breadth-first propagation
        queue = []
        visited = set()
        
        # Start from nodes closest to the base station
        for node in self.nodes:
            if node.alive:
                distance = node.distance_to(self.base_station)
                if distance <= 20:  # assume base station has longer range
                    queue.append((node, 1))  # (node, hop_count)
                    visited.add(node.id)
        
        # Propagate interest
        while queue:
            current_node, hop_count = queue.pop(0)
            
            # Energy consumption for receiving interest
            current_node.receive(100)  # interest packet size
            
            # Propagate to neighbors
            for neighbor in current_node.neighbors:
                if neighbor.alive and neighbor.id not in visited:
                    # Initialize gradient
                    self.gradients[neighbor][current_node] = 1.0 / hop_count
                    
                    # Add to queue
                    queue.append((neighbor, hop_count + 1))
                    visited.add(neighbor.id)
                    
                    # Energy consumption for transmitting interest
                    distance = current_node.distance_to(neighbor)
                    current_node.transmit(100, distance)
        
        yield self.env.timeout(20)  # interest propagation takes time
    
    def detect_events(self):
        """Simulate event detection at random nodes"""
        for node in self.nodes:
            if node.alive and random.random() < 0.01:  # 1% chance of event detection
                self.events_detected[node.id] = self.env.now
                node.sense(self.packet_size)  # sensing consumes energy
        
        yield self.env.timeout(5)
    
    def deliver_data(self):
        """Deliver detected data along gradients"""
        for node_id, event_time in list(self.events_detected.items()):
            # Check if event is recent
            if self.env.now - event_time > 50:  # event expires after 50 time units
                del self.events_detected[node_id]
                continue
                
            # Find the node
            node = next((n for n in self.nodes if n.id == node_id), None)
            if not node or not node.alive:
                continue
                
            # Forward data along gradient
            current_node = node
            visited = set([node.id])
            data_size = self.packet_size
            
            while True:
                # Find best next hop based on gradients
                if current_node not in self.gradients:
                    break
                    
                next_hop = None
                max_gradient = 0
                
                for neighbor, gradient in self.gradients[current_node].items():
                    if neighbor.alive and neighbor.id not in visited and gradient > max_gradient:
                        max_gradient = gradient
                        next_hop = neighbor
                
                if not next_hop:
                    # No viable next hop
                    break
                
                # Transmit data to next hop
                distance = current_node.distance_to(next_hop)
                if not current_node.transmit(data_size, distance):
                    # Node died during transmission
                    break
                    
                if not next_hop.receive(data_size):
                    # Next hop died during reception
                    break
                
                # Move to next hop
                visited.add(next_hop.id)
                current_node = next_hop
                
                # If next hop is close to base station, deliver data
                if current_node.distance_to(self.base_station) <= 20:
                    # Deliver to base station
                    distance = current_node.distance_to(self.base_station)
                    if current_node.transmit(data_size, distance):
                        self.base_station.receive_data(data_size)
                    break
        
        yield self.env.timeout(10)
    
    def reinforce_paths(self):
        """Reinforce successful paths"""
        # Simple reinforcement: increase gradient for neighbors that delivered data
        for node in self.nodes:
            if not node.alive:
                continue
                
            if node in self.gradients:
                # Normalize gradients
                total = sum(self.gradients[node].values()) or 1
                for neighbor in self.gradients[node]:
                    self.gradients[node][neighbor] /= total
                    
                    # Small reinforcement message
                    if node.alive and neighbor.alive:
                        distance = node.distance_to(neighbor)
                        node.transmit(50, distance)
                        neighbor.receive(50)
        
        yield self.env.timeout(10)