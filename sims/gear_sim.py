# gear_sim.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

def distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def transmit_energy(k, dist, config):
    if dist < config['THRESH_DIST']:
        return k * config['E_ELEC'] + k * config['E_FS'] * dist**2
    else:
        return k * config['E_ELEC'] + k * config['E_MP'] * dist**4

def receive_energy(k, config):
    return k * config['E_ELEC']

def initialize_nodes(config):
    return {
        'x': np.random.uniform(0, config['FIELD_X'], config['NUM_NODES']),
        'y': np.random.uniform(0, config['FIELD_Y'], config['NUM_NODES']),
        'energy': np.full(config['NUM_NODES'], config['INIT_ENERGY']),
        'alive': np.full(config['NUM_NODES'], True),
    }

def simulate_gear(config=None):
    """Simulate GEAR protocol with configurable parameters"""
    # Use default config if none provided
    if config is None:
        from config import get_simulation_parameters
        config = get_simulation_parameters()
    
    # GEAR-specific parameters
    if 'COMM_RANGE' not in config:
        config['COMM_RANGE'] = 30  # Default communication range
    
    nodes = initialize_nodes(config)
    alive_history, energy_history = [], []
    plot_area = st.empty()

    for r in range(config['ROUNDS']):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break

        # Select nodes within communication range of sink
        dist_to_sink = distance(nodes['x'], nodes['y'], *config['SINK_POS'])
        in_range = np.where((dist_to_sink < config['COMM_RANGE'] * 3) & nodes['alive'])[0]

        if len(in_range) == 0:
            # Find closest 5 alive nodes
            alive_indices = np.where(nodes['alive'])[0]
            if len(alive_indices) > 0:
                distances = dist_to_sink[alive_indices]
                closest_indices = np.argsort(distances)[:min(5, len(alive_indices))]
                in_range = alive_indices[closest_indices]

        # Add this after the in_range calculation:
        st.sidebar.write(f"Round {r+1}: {len(in_range)} nodes in range")
        
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, config['FIELD_X'])
        ax.set_ylim(0, config['FIELD_Y'] + 60)
        ax.set_title(f"GEAR - Round {r+1}")
        ax.plot(config['SINK_POS'][0], config['SINK_POS'][1], '*k', markersize=12)

        for i in range(config['NUM_NODES']):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        # Communication from nodes to sink within range
        for i in in_range:
            d = distance(nodes['x'][i], nodes['y'][i], *config['SINK_POS'])
            e = transmit_energy(config['PACKET_SIZE'], d, config) + config['E_DA'] * config['PACKET_SIZE']
            nodes['energy'][i] -= e
            ax.plot([nodes['x'][i], config['SINK_POS'][0]], 
                    [nodes['y'][i], config['SINK_POS'][1]], 'g--', lw=0.5)

        nodes['alive'] = nodes['energy'] > 0
        alive_history.append(np.sum(nodes['alive']))
        energy_history.append(np.sum(nodes['energy'][nodes['alive']]))
        plot_area.pyplot(fig)
        plt.close(fig)
        time.sleep(0.4)

    return alive_history, energy_history

if __name__ == "__main__":
    st.title("GEAR Protocol Simulation")
    
    # Allow protocol-specific parameters
    with st.sidebar.expander("GEAR Parameters", expanded=True):
        comm_range = st.slider("Communication Range", 10, 50, 30)
    
    # Get common parameters
    from config import get_simulation_parameters
    config = get_simulation_parameters()
    config['COMM_RANGE'] = comm_range
    
    if st.button("Run GEAR Simulation"):
        with st.spinner("Simulating GEAR..."):
            alive, energy = simulate_gear(config)
        fig, axs = plt.subplots(2, 1, figsize=(10, 6))
        axs[0].plot(alive)
        axs[0].set_title("Alive Nodes")
        axs[1].plot(energy, color='orange')
        axs[1].set_title("Total Energy")
        for ax in axs: ax.set_xlabel("Round")
        st.pyplot(fig)
        plt.close(fig)