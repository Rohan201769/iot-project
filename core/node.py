import numpy as np
from utils.energy_model import EnergyModel

class SensorNode:
    """Base class for a wireless sensor node"""
    
    def __init__(self, env, node_id, position, initial_energy=1.0):
        self.env = env
        self.id = node_id
        self.position = position  # (x, y) tuple
        self.energy = initial_energy  # normalized energy level (0.0 to 1.0)
        self.alive = True
        self.data_queue = []
        self.neighbors = []
        self.cluster_head = None
        self.is_cluster_head = False
        self.protocol = None
        self.energy_model = EnergyModel()
        
    def transmit(self, data_size, distance):
        """Consume energy for data transmission
        
        Args:
            data_size: Size of data in bits
            distance: Distance to receiver in meters
        
        Returns:
            bool: True if transmission was successful, False if node died
        """
        if not self.alive:
            return False
            
        energy_cost = self.energy_model.calculate_tx_energy(data_size, distance)
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            if self.energy <= 0:
                self.energy = 0
                self.alive = False
            return True
        else:
            self.energy = 0
            self.alive = False
            return False
    
    def receive(self, data_size):
        """Consume energy for data reception
        
        Args:
            data_size: Size of data in bits
        
        Returns:
            bool: True if reception was successful, False if node died
        """
        if not self.alive:
            return False
            
        energy_cost = self.energy_model.calculate_rx_energy(data_size)
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            if self.energy <= 0:
                self.energy = 0
                self.alive = False
            return True
        else:
            self.energy = 0
            self.alive = False
            return False
    
    def sense(self, data_size):
        """Consume energy for sensing data
        
        Args:
            data_size: Size of data in bits
        
        Returns:
            bool: True if sensing was successful, False if node died
        """
        if not self.alive:
            return False
            
        energy_cost = self.energy_model.calculate_sensing_energy(data_size)
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            if self.energy <= 0:
                self.energy = 0
                self.alive = False
            return True
        else:
            self.energy = 0
            self.alive = False
            return False
    
    def aggregate_data(self, data_size):
        """Consume energy for data aggregation
        
        Args:
            data_size: Size of data in bits
        
        Returns:
            bool: True if aggregation was successful, False if node died
        """
        if not self.alive:
            return False
            
        energy_cost = self.energy_model.calculate_aggregation_energy(data_size)
        if self.energy >= energy_cost:
            self.energy -= energy_cost
            if self.energy <= 0:
                self.energy = 0
                self.alive = False
            return True
        else:
            self.energy = 0
            self.alive = False
            return False
            
    def distance_to(self, other_node):
        """Calculate Euclidean distance to another node
        
        Args:
            other_node: Another SensorNode or object with position attribute
            
        Returns:
            float: Euclidean distance between nodes
        """
        return np.sqrt((self.position[0] - other_node.position[0])**2 + 
                     (self.position[1] - other_node.position[1])**2)