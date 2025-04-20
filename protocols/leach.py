import random
from collections import defaultdict
from protocols.base_protocol import RoutingProtocol

class LEACH(RoutingProtocol):
    """Low-Energy Adaptive Clustering Hierarchy protocol implementation"""
    
    def __init__(self, simulation, p=0.05, round_time=100):
        """Initialize LEACH protocol
        
        Args:
            simulation: WSNSimulation instance
            p: Probability of becoming a cluster head
            round_time: Duration of each round
        """
        super().__init__(simulation)
        self.p = p  # probability of becoming cluster head
        self.round_time = round_time
        self.current_round = 0
        self.cluster_heads = []
        self.clusters = defaultdict(list)  # CH -> [member nodes]
        
    def setup(self):
        """Setup LEACH protocol"""
        # Reset cluster head status for all nodes
        for node in self.nodes:
            node.is_cluster_head = False
            node.cluster_head = None
        
    def run(self):
        """Execute LEACH protocol"""
        while True:
            # Start new round
            self.current_round += 1
            yield self.env.process(self.setup_phase())
            yield self.env.process(self.steady_state_phase())
            
            # Wait for next round
            yield self.env.timeout(self.round_time)
    
    def setup_phase(self):
        """Setup phase: elect cluster heads and form clusters"""
        # Reset clusters
        self.cluster_heads = []
        self.clusters = defaultdict(list)
        
        # Reset cluster head status for all nodes
        for node in self.nodes:
            node.is_cluster_head = False
            node.cluster_head = None
        
        # Elect cluster heads
        for node in self.nodes:
            if not node.alive:
                continue
                
            # Threshold based on LEACH algorithm
            t = self.p / (1 - self.p * (self.current_round % int(1/self.p)))
            if random.random() < t:
                node.is_cluster_head = True
                self.cluster_heads.append(node)
        
        # Broadcast cluster head status
        for ch in self.cluster_heads:
            # Simulated broadcast - energy consumption
            for node in self.nodes:
                if node != ch and node.alive:
                    distance = ch.distance_to(node)
                    ch.transmit(50, distance)  # small message size
        
        # Non-CH nodes join nearest cluster head
        for node in self.nodes:
            if not node.alive or node.is_cluster_head:
                continue
                
            # Find nearest cluster head
            min_distance = float('inf')
            nearest_ch = None
            for ch in self.cluster_heads:
                distance = node.distance_to(ch)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ch = ch
            
            if nearest_ch:
                node.cluster_head = nearest_ch
                self.clusters[nearest_ch].append(node)
                
                # Send join message
                node.transmit(50, min_distance)
                nearest_ch.receive(50)
        
        # Create TDMA schedule
        for ch in self.cluster_heads:
            if not ch.alive:
                continue
                
            members = self.clusters[ch]
            # Send TDMA schedule to members
            for node in members:
                distance = ch.distance_to(node)
                ch.transmit(100, distance)  # schedule message
                node.receive(100)
        
        yield self.env.timeout(10)  # setup phase takes time
    
    def steady_state_phase(self):
        """Steady state phase: collect and transmit data"""
        # Each round has multiple frames
        num_frames = 5
        
        for _ in range(num_frames):
            # Each node sends data to its cluster head according to TDMA schedule
            for ch in self.cluster_heads:
                if not ch.alive:
                    continue
                    
                # Collect data from cluster members
                data_collected = 0
                for node in self.clusters[ch]:
                    if not node.alive:
                        continue
                        
                    # Node senses data
                    if node.sense(self.packet_size):
                        # Node transmits data to CH
                        distance = node.distance_to(ch)
                        if node.transmit(self.packet_size, distance):
                            # CH receives data
                            if ch.receive(self.packet_size):
                                data_collected += self.packet_size
                
                # Cluster head aggregates data
                if data_collected > 0:
                    aggregated_size = data_collected * 0.7  # assume 30% reduction from aggregation
                    if ch.aggregate_data(data_collected):
                        # Transmit to base station
                        distance = ch.distance_to(self.base_station)
                        if ch.transmit(aggregated_size, distance):
                            self.base_station.receive_data(aggregated_size)
            
            yield self.env.timeout(20)  # frame time
            
        yield self.env.timeout(50)  # steady state phase