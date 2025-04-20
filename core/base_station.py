class BaseStation:
    """Base station/sink node in a wireless sensor network"""
    
    def __init__(self, position):
        """Initialize a base station
        
        Args:
            position: (x, y) tuple representing the position of the base station
        """
        self.position = position
        self.data_received = 0
        self.packets_received = 0
        self.id = "BS"  # Special ID for the base station
        
    def receive_data(self, data_size):
        """Record received data
        
        Args:
            data_size: Size of received data in bits
        """
        self.data_received += data_size
        self.packets_received += 1
        
    def distance_to(self, node):
        """Calculate Euclidean distance to a node
        
        Args:
            node: A SensorNode or object with position attribute
            
        Returns:
            float: Euclidean distance to the node
        """
        return ((self.position[0] - node.position[0])**2 + 
                (self.position[1] - node.position[1])**2)**0.5