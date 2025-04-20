class RoutingProtocol:
    """Base class for all routing protocols"""
    
    def __init__(self, simulation):
        """Initialize the routing protocol
        
        Args:
            simulation: A reference to the WSNSimulation instance
        """
        self.simulation = simulation
        self.env = simulation.env
        self.nodes = simulation.nodes
        self.base_station = simulation.base_station
        self.packet_size = simulation.packet_size
        
    def setup(self):
        """Setup the protocol (e.g., initialize data structures)"""
        pass
    
    def run(self):
        """Main protocol execution - to be implemented by subclasses"""
        pass
        
    def get_name(self):
        """Get the name of the protocol
        
        Returns:
            str: Name of the protocol
        """
        return self.__class__.__name__