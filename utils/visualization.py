import random
import numpy as np
import simpy
from core.node import SensorNode
from core.base_station import BaseStation
from protocols.leach import LEACH
from protocols.directed_diffusion import DirectedDiffusion
from protocols.gear import GEAR
from protocols.pegasis import PEGASIS

class WSNSimulation:
    """Main simulation environment for Wireless Sensor Networks"""
    
    def __init__(self, config):
        """Initialize the simulation environment
        
        Args:
            config: A dictionary containing simulation parameters
        """
        self.env = simpy.Environment()
        self.width = config.get('width', 100)
        self.height = config.get('height', 100)
        self.num_nodes = config.get('num_nodes', 100)
        self.base_station_pos = config.get('base_station_pos', (50, 50))
        self.protocol_type = config.get('protocol_type', 'LEACH')
        self.simulation_time = config.get('simulation_time', 1000)
        self.packet_size = config.get('packet_size', 4000)
        self.comm_range = config.get('comm_range', 30)
        self.seed = config.get('seed', None)
        
        # Set random seed if provided
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)
        
        # Create base station
        self.base_station = BaseStation(self.base_station_pos)
        
        # Create nodes
        self.nodes = []
        
        # Metrics
        self.metrics = {
            'alive_nodes': [],
            'energy_levels': [],
            'packets_delivered': 0,
            'network_lifetime': 0,
            'total_energy_consumed': 0,
            'time_points': []
        }
        
        # Initialize nodes and protocol
        self._create_nodes()
        self._setup_protocol()
        
    def _create_nodes(self):
        """Create sensor nodes with random positions"""
        for i in range(self.num_nodes):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            node = SensorNode(self.env, i, (x, y))
            self.nodes.append(node)
            
        # Set up neighbors for each node (based on communication range)
        for node in self.nodes:
            for other in self.nodes:
                if node != other and node.distance_to(other) <= self.comm_range:
                    node.neighbors.append(other)
    
    def _setup_protocol(self):
        """Initialize routing protocol based on type"""
        if self.protocol_type == "LEACH":
            self.protocol = LEACH(self)
        elif self.protocol_type == "DirectedDiffusion":
            self.protocol = DirectedDiffusion(self)
        elif self.protocol_type == "GEAR":
            self.protocol = GEAR(self)
        elif self.protocol_type == "PEGASIS":
            self.protocol = PEGASIS(self)
        else:
            raise ValueError(f"Unknown protocol type: {self.protocol_type}")
            
        # Setup protocol
        self.protocol.setup()
    
    def run(self):
        """Run the simulation
        
        Returns:
            dict: Collected metrics
        """
        # Setup protocol process
        self.env.process(self.protocol.run())
        
        # Setup data collection process
        self.env.process(self.collect_metrics())
        
        # Run for specified time
        self.env.run(until=self.simulation_time)
        
        return self.metrics
    
    def collect_metrics(self):
        """Collect simulation metrics periodically"""
        while True:
            # Record time point
            self.metrics['time_points'].append(self.env.now)
            
            # Count alive nodes
            alive = sum(1 for node in self.nodes if node.alive)
            self.metrics['alive_nodes'].append(alive)
            
            # Average energy level
            avg_energy = sum(node.energy for node in self.nodes) / self.num_nodes
            self.metrics['energy_levels'].append(avg_energy)
            
            # Record packets delivered
            self.metrics['packets_delivered'] = self.base_station.packets_received
            
            # If no nodes alive, record network lifetime
            if alive == 0 and self.metrics['network_lifetime'] == 0:
                self.metrics['network_lifetime'] = self.env.now
            
            # Calculate total energy consumed
            initial_energy = self.num_nodes  # assuming each node starts with 1.0
            current_energy = sum(node.energy for node in self.nodes)
            self.metrics['total_energy_consumed'] = initial_energy - current_energy
            
            yield self.env.timeout(10)  # collect every 10 time units