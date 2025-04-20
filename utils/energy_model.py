# Energy model for wireless sensor networks
class EnergyModel:
    """Energy consumption model for wireless sensor networks"""
    
    def __init__(self):
        # Energy consumption parameters in Joules
        self.e_elec = 50e-9      # Energy for electronics (J/bit)
        self.e_amp = 100e-12     # Energy for amplifier (J/bit/m^2)
        self.e_da = 5e-9         # Energy for data aggregation (J/bit)
        self.e_sense = 5e-9      # Energy for sensing (J/bit)
        
    def calculate_tx_energy(self, data_size, distance):
        """Calculate energy required for transmitting data"""
        return (self.e_elec * data_size) + (self.e_amp * data_size * (distance ** 2))
    
    def calculate_rx_energy(self, data_size):
        """Calculate energy required for receiving data"""
        return self.e_elec * data_size
    
    def calculate_sensing_energy(self, data_size):
        """Calculate energy required for sensing data"""
        return self.e_sense * data_size
    
    def calculate_aggregation_energy(self, data_size):
        """Calculate energy required for data aggregation"""
        return self.e_da * data_size