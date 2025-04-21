import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Constants ---
NUM_NODES = 100
FIELD_X, FIELD_Y = 100, 100
SINK_POS = (50, 150)
INIT_ENERGY = 0.5
E_ELEC = 50e-9
E_FS = 10e-12
E_MP = 0.0013e-12
E_DA = 5e-9
THRESH_DIST = np.sqrt(E_FS / E_MP)
ROUNDS = 50

# --- Directed Diffusion Specific ---
INTEREST_DURATION = 10

def distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def transmit_energy(k, dist):
    if dist < THRESH_DIST:
        return k * E_ELEC + k * E_FS * dist**2
    else:
        return k * E_ELEC + k * E_MP * dist**4

def receive_energy(k):
    return k * E_ELEC

def initialize_nodes():
    return {
        'x': np.random.uniform(0, FIELD_X, NUM_NODES),
        'y': np.random.uniform(0, FIELD_Y, NUM_NODES),
        'energy': np.full(NUM_NODES, INIT_ENERGY),
        'alive': np.full(NUM_NODES, True),
        'interested': np.zeros(NUM_NODES),  # Interest flag
    }

def simulate_directed_diffusion():
    nodes = initialize_nodes()
    alive_history, energy_history = [], []
    plot_area = st.empty()

    for r in range(ROUNDS):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break

        # Randomly select nodes to send interest and data
        if r % INTEREST_DURATION == 0:
            interested_nodes = np.random.choice(np.where(nodes['alive'])[0], size=5, replace=False)
            nodes['interested'] = np.zeros(NUM_NODES)
            nodes['interested'][interested_nodes] = 1

        # Collect the data
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, FIELD_X)
        ax.set_ylim(0, FIELD_Y + 60)
        ax.set_title(f"Directed Diffusion - Round {r+1}")
        ax.plot(SINK_POS[0], SINK_POS[1], '*k', markersize=12)

        for i in range(NUM_NODES):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            elif nodes['interested'][i] == 1:
                ax.plot(nodes['x'][i], nodes['y'][i], 'rs')  # Interested node
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        # Send interest and data
        for i in np.where(nodes['interested'])[0]:
            d = distance(nodes['x'][i], nodes['y'][i], *SINK_POS)
            e = transmit_energy(4000, d) + E_DA * 4000
            nodes['energy'][i] -= e
            ax.plot([nodes['x'][i], SINK_POS[0]], [nodes['y'][i], SINK_POS[1]], 'g--', lw=0.5)

        nodes['alive'] = nodes['energy'] > 0
        alive_history.append(np.sum(nodes['alive']))
        energy_history.append(np.sum(nodes['energy'][nodes['alive']]))
        plot_area.pyplot(fig)
        plt.close(fig)
        time.sleep(0.4)

    return alive_history, energy_history

# --- Streamlit UI ---

st.title("Directed Diffusion Protocol Simulation")

st.markdown("""
Directed Diffusion is based on the concept of interest propagation. Nodes send interest to the source,
and once the data is available, the nodes collect and relay it to the sink.
""")

if st.button("Run Directed Diffusion Simulation"):
    with st.spinner("Simulating Directed Diffusion..."):
        alive, energy = simulate_directed_diffusion()
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))
    axs[0].plot(alive)
    axs[0].set_title("Alive Nodes")
    axs[1].plot(energy, color='orange')
    axs[1].set_title("Total Energy")
    for ax in axs: ax.set_xlabel("Round")
    st.pyplot(fig)
    plt.close(fig)
