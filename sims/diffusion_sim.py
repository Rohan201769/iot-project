# diffusion_sim.py
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
        'interested': np.zeros(config['NUM_NODES']),  # Interest flag
    }

def simulate_directed_diffusion(config=None):
    """Simulate Directed Diffusion protocol with configurable parameters"""
    # Use default config if none provided
    if config is None:
        from config import get_simulation_parameters
        config = get_simulation_parameters()
    
    # Directed Diffusion specific parameters
    if 'INTEREST_DURATION' not in config:
        config['INTEREST_DURATION'] = 10  # Default interest duration
    if 'INTEREST_NODES' not in config:
        config['INTEREST_NODES'] = 5  # Default number of interested nodes
    
    nodes = initialize_nodes(config)
    alive_history, energy_history = [], []
    plot_area = st.empty()

    for r in range(config['ROUNDS']):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break

        # Randomly select nodes to send interest and data
        if r % config['INTEREST_DURATION'] == 0:
            if len(alive_idx) >= config['INTEREST_NODES']:
                interested_nodes = np.random.choice(
                    alive_idx, 
                    size=config['INTEREST_NODES'], 
                    replace=False
                )
            else:
                interested_nodes = alive_idx
                
            nodes['interested'] = np.zeros(config['NUM_NODES'])
            nodes['interested'][interested_nodes] = 1

        # Collect the data
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, config['FIELD_X'])
        ax.set_ylim(0, config['FIELD_Y'] + 60)
        ax.set_title(f"Directed Diffusion - Round {r+1}")
        ax.plot(config['SINK_POS'][0], config['SINK_POS'][1], '*k', markersize=12)

        for i in range(config['NUM_NODES']):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            elif nodes['interested'][i] == 1:
                ax.plot(nodes['x'][i], nodes['y'][i], 'rs')  # Interested node
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        # Send interest and data
        for i in np.where(nodes['interested'])[0]:
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
    st.title("Directed Diffusion Protocol Simulation")
    
    # Allow protocol-specific parameters
    with st.sidebar.expander("Directed Diffusion Parameters", expanded=True):
        interest_duration = st.slider("Interest Duration (rounds)", 1, 20, 10)
        interest_nodes = st.slider("Number of Interest Nodes", 1, 20, 5)
    
    # Get common parameters
    from config import get_simulation_parameters
    config = get_simulation_parameters()
    config['INTEREST_DURATION'] = interest_duration
    config['INTEREST_NODES'] = interest_nodes
    
    if st.button("Run Directed Diffusion Simulation"):
        with st.spinner("Simulating Directed Diffusion..."):
            alive, energy = simulate_directed_diffusion(config)
        fig, axs = plt.subplots(2, 1, figsize=(10, 6))
        axs[0].plot(alive)
        axs[0].set_title("Alive Nodes")
        axs[1].plot(energy, color='orange')
        axs[1].set_title("Total Energy")
        for ax in axs: ax.set_xlabel("Round")
        st.pyplot(fig)
        plt.close(fig)