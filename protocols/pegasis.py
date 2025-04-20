import numpy as np
from protocols.base_protocol import RoutingProtocol

class PEGASIS(RoutingProtocol):
    """Implementation of the PEGASIS protocol"""
    
    def __init__(self, simulation, chain_reconstruction_interval=500):
        """Initialize PEGASIS protocol
        
        Args:
            simulation: WSNSimulation instance
            chain_reconstruction_interval: Interval for chain reconstruction
        """
        super().__init__(simulation)
        self.chain = []  # ordered list of nodes in the chain
        self.leader = None  # current chain leader
        self.chain_reconstruction_interval = chain_reconstruction_interval
        
    def setup(self):
        """Setup PEGASIS protocol"""
        # Initial chain construction
        self.construct_chain()
        
    def run(self):
        """Execute PEGASIS protocol"""
        # Main protocol loop
        round_num = 0
        while True:
            # Select leader for this round
            round_num += 1
            if self.chain:
                self.leader = self.chain[round_num % len(self.chain)]
            
            # Gather and aggregate data along the chain
            if self.chain and self.leader and self.leader.alive:
                yield self.env.process(self.gather_data())
            
            # Periodically reconstruct chain to adapt to dead nodes
            if self.env.now % self.chain_reconstruction_interval == 0:
                self.construct_chain()
            
            yield self.env.timeout(50)  # round time
    
    def construct_chain(self):
        """Construct a chain using greedy algorithm"""
        alive_nodes = [node for node in self.nodes if node.alive]
        if not alive_nodes:
            self.chain = []
            self.leader = None
            return
            
        # Start from the furthest node from the base station
        max_distance = -1
        start_node = None
        
        for node in alive_nodes:
            distance = node.distance_to(self.base_station)
            if distance > max_distance:
                max_distance = distance
                start_node = node
        
        # Construct chain greedily
        self.chain = [start_node]
        remaining_nodes = set(alive_nodes) - {start_node}
        
        while remaining_nodes:
            last_node = self.chain[-1]
            next_node = None
            min_distance = float('inf')
            
            for node in remaining_nodes:
                distance = last_node.distance_to(node)
                if distance < min_distance:
                    min_distance = distance
                    next_node = node
            
            if next_node:
                self.chain.append(next_node)
                remaining_nodes.remove(next_node)
            else:
                break
    
    def gather_data(self):
        """Gather and aggregate data along the chain"""
        if not self.chain or not self.leader or not self.leader.alive:
            yield self.env.timeout(10)
            return
            
        # Find leader's position in chain
        try:
            leader_idx = self.chain.index(self.leader)
        except ValueError:
            # Leader not in chain (e.g., died after selection)
            yield self.env.timeout(10)
            return
            
        # Data gathering in both directions from the leader
        # First direction: from leader to start of chain
        data_size = 0
        current_idx = leader_idx - 1
        
        while current_idx >= 0:
            current = self.chain[current_idx]
            next_idx = current_idx + 1
            next_node = self.chain[next_idx]
            
            if not current.alive or not next_node.alive:
                break
                
            # Sense data
            if current.sense(self.packet_size):
                data_size += self.packet_size
                
                # Transmit to next node
                distance = current.distance_to(next_node)
                if not current.transmit(self.packet_size, distance):
                    break
                    
                if not next_node.receive(self.packet_size):
                    break
            
            current_idx -= 1
            
        # Second direction: from leader to end of chain
        current_idx = leader_idx + 1
        
        while current_idx < len(self.chain):
            current = self.chain[current_idx]
            next_idx = current_idx - 1
            next_node = self.chain[next_idx]
            
            if not current.alive or not next_node.alive:
                break
                
            # Sense data
            if current.sense(self.packet_size):
                data_size += self.packet_size
                
                # Transmit to next node
                distance = current.distance_to(next_node)
                if not current.transmit(self.packet_size, distance):
                    break
                    
                if not next_node.receive(self.packet_size):
                    break
            
            current_idx += 1
        
        # Leader aggregates all data
        if data_size > 0 and self.leader.alive:
            # Assume 30% reduction from aggregation
            aggregated_size = data_size * 0.7
            if self.leader.aggregate_data(data_size):
                # Transmit to base station
                distance = self.leader.distance_to(self.base_station)
                if self.leader.transmit(aggregated_size, distance):
                    self.base_station.receive_data(aggregated_size)
        
        yield self.env.timeout(30)  # data gathering takes time