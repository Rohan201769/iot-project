# leach_sim.py
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

def simulate_leach(config=None):
    """Simulate LEACH protocol with configurable parameters"""
    # Use default config if none provided
    if config is None:
        from config import get_simulation_parameters
        config = get_simulation_parameters()
    
    # Get LEACH-specific parameters
    if 'P_CH' not in config:
        config['P_CH'] = 0.05  # Default probability of becoming CH
    
    nodes = initialize_nodes(config)
    alive_history, energy_history, ch_history = [], [], []
    plot_area = st.empty()

    for r in range(config['ROUNDS']):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break
        ch_prob = np.random.rand(len(alive_idx))
        ch_idx = alive_idx[ch_prob < config['P_CH']]
        ch_history.append(len(ch_idx))

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, config['FIELD_X'])
        ax.set_ylim(0, config['FIELD_Y'] + 60)
        ax.set_title(f"LEACH - Round {r+1}")
        ax.plot(config['SINK_POS'][0], config['SINK_POS'][1], '*k', markersize=12)

        for i in range(config['NUM_NODES']):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            elif i in ch_idx:
                ax.plot(nodes['x'][i], nodes['y'][i], 'rs')
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        for i in alive_idx:
            if i in ch_idx:
                d = distance(nodes['x'][i], nodes['y'][i], *config['SINK_POS'])
                e = transmit_energy(config['PACKET_SIZE'], d, config) + config['E_DA'] * config['PACKET_SIZE']
                nodes['energy'][i] -= e
                ax.plot([nodes['x'][i], config['SINK_POS'][0]], 
                        [nodes['y'][i], config['SINK_POS'][1]], 'g--', lw=0.5)
            else:
                if len(ch_idx) == 0: continue
                dists = distance(nodes['x'][i], nodes['y'][i], nodes['x'][ch_idx], nodes['y'][ch_idx])
                ch_id = ch_idx[np.argmin(dists)]
                dist = dists.min()
                nodes['energy'][i] -= transmit_energy(config['PACKET_SIZE'], dist, config)
                nodes['energy'][ch_id] -= receive_energy(config['PACKET_SIZE'], config)
                ax.plot([nodes['x'][i], nodes['x'][ch_id]], 
                        [nodes['y'][i], nodes['y'][ch_id]], 'y-', lw=0.3)

        nodes['alive'] = nodes['energy'] > 0
        alive_history.append(np.sum(nodes['alive']))
        energy_history.append(np.sum(nodes['energy'][nodes['alive']]))
        plot_area.pyplot(fig)
        plt.close(fig)
        time.sleep(0.4)

    return alive_history, energy_history, ch_history

if __name__ == "__main__":
    st.title("LEACH Protocol Simulation")
    
    # Allow protocol-specific parameters
    with st.sidebar.expander("LEACH Parameters", expanded=True):
        p_ch = st.slider("Cluster Head Probability", 0.01, 0.2, 0.05, step=0.01)
    
    # Get common parameters
    from config import get_simulation_parameters
    config = get_simulation_parameters()
    config['P_CH'] = p_ch
    
    if st.button("Run LEACH Simulation"):
        with st.spinner("Simulating LEACH..."):
            alive, energy, ch = simulate_leach(config)
        fig, axs = plt.subplots(3, 1, figsize=(10, 10))
        axs[0].plot(alive)
        axs[0].set_title("Alive Nodes")
        axs[1].plot(energy, color='orange')
        axs[1].set_title("Total Energy")
        axs[2].plot(ch, color='green')
        axs[2].set_title("CHs per Round")
        for ax in axs: ax.set_xlabel("Round")
        st.pyplot(fig)
        plt.close(fig)