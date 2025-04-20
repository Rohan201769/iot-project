"""Configuration settings for WSN simulations"""

# Default configuration
DEFAULT_CONFIG = {
    # Network parameters
    'width': 100,                # Width of simulation area
    'height': 100,               # Height of simulation area
    'num_nodes': 100,            # Number of sensor nodes
    'base_station_pos': (50, 50), # Position of base station
    'comm_range': 30,            # Communication range of nodes
    
    # Simulation parameters
    'simulation_time': 1000,     # Total simulation time
    'packet_size': 4000,         # Size of data packets in bits
    'seed': 42,                  # Random seed for reproducibility
    
    # Protocol-specific parameters
    'protocol_type': 'LEACH',    # Default protocol
    
    # LEACH parameters
    'leach_p': 0.05,             # Probability of becoming cluster head
    'leach_round_time': 100,     # Duration of each round
    
    # Directed Diffusion parameters
    'dd_interest_interval': 200, # Interval for interest propagation
    'dd_reinforcement_interval': 50, # Interval for path reinforcement
    
    # GEAR parameters
    'gear_interest_interval': 200, # Interval for interest propagation
    
    # PEGASIS parameters
    'pegasis_chain_interval': 500 # Interval for chain reconstruction
}

# Different network sizes
SMALL_NETWORK = {
    'num_nodes': 30,
    'width': 50,
    'height': 50,
    'comm_range': 20
}

MEDIUM_NETWORK = {
    'num_nodes': 100,
    'width': 100,
    'height': 100,
    'comm_range': 30
}

LARGE_NETWORK = {
    'num_nodes': 300,
    'width': 200,
    'height': 200,
    'comm_range': 40
}

# Different simulation durations
SHORT_SIMULATION = {
    'simulation_time': 500
}

LONG_SIMULATION = {
    'simulation_time': 2000
}

# Different energy scenarios
HIGH_TRAFFIC = {
    'packet_size': 8000
}

LOW_TRAFFIC = {
    'packet_size': 2000
}

def get_config(config_name=None):
    """Get configuration based on name
    
    Args:
        config_name: Name of configuration or None for default
        
    Returns:
        dict: Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_name == 'small':
        config.update(SMALL_NETWORK)
    elif config_name == 'medium':
        config.update(MEDIUM_NETWORK)
    elif config_name == 'large':
        config.update(LARGE_NETWORK)
    elif config_name == 'short':
        config.update(SHORT_SIMULATION)
    elif config_name == 'long':
        config.update(LONG_SIMULATION)
    elif config_name == 'high_traffic':
        config.update(HIGH_TRAFFIC)
    elif config_name == 'low_traffic':
        config.update(LOW_TRAFFIC)
    
    return config