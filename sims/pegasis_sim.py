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
    }

def form_chain(nodes):
    chain = []
    unvisited = list(np.where(nodes['alive'])[0])
    if not unvisited:
        return chain
    current = unvisited.pop(0)
    chain.append(current)
    while unvisited:
        dists = distance(nodes['x'][current], nodes['y'][current], nodes['x'][unvisited], nodes['y'][unvisited])
        next_idx = unvisited[np.argmin(dists)]
        chain.append(next_idx)
        unvisited.remove(next_idx)
        current = next_idx
    return chain

def simulate_pegasis():
    nodes = initialize_nodes()
    alive_history, energy_history = [], []
    plot_area = st.empty()

    for r in range(ROUNDS):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break

        chain = form_chain(nodes)
        leader_idx = chain[r % len(chain)] if chain else None

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, FIELD_X)
        ax.set_ylim(0, FIELD_Y + 60)
        ax.set_title(f"PEGASIS - Round {r+1}")
        ax.plot(SINK_POS[0], SINK_POS[1], '*k', markersize=12)

        for i in range(NUM_NODES):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            elif i == leader_idx:
                ax.plot(nodes['x'][i], nodes['y'][i], 'rs')
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        # Chain communication
        for i in range(len(chain) - 1):
            n1, n2 = chain[i], chain[i+1]
            d = distance(nodes['x'][n1], nodes['y'][n1], nodes['x'][n2], nodes['y'][n2])
            e_tx = transmit_energy(4000, d)
            e_rx = receive_energy(4000)
            nodes['energy'][n1] -= e_tx
            nodes['energy'][n2] -= e_rx
            ax.plot([nodes['x'][n1], nodes['x'][n2]], [nodes['y'][n1], nodes['y'][n2]], 'y-', lw=0.3)

        # Leader sends to sink
        if leader_idx is not None:
            d = distance(nodes['x'][leader_idx], nodes['y'][leader_idx], *SINK_POS)
            e = transmit_energy(4000, d) + E_DA * 4000
            nodes['energy'][leader_idx] -= e
            ax.plot([nodes['x'][leader_idx], SINK_POS[0]], [nodes['y'][leader_idx], SINK_POS[1]], 'g--', lw=0.5)

        nodes['alive'] = nodes['energy'] > 0
        alive_history.append(np.sum(nodes['alive']))
        energy_history.append(np.sum(nodes['energy'][nodes['alive']]))
        plot_area.pyplot(fig)
        plt.close(fig)
        time.sleep(0.4)

    return alive_history, energy_history

# --- Streamlit UI ---

st.title("PEGASIS Protocol Simulation")

st.markdown("""
PEGASIS (Power-Efficient GAthering in Sensor Information System) forms a chain of sensor nodes.
Each round, a different node becomes the chain leader and communicates with the sink.
""")

if st.button("Run PEGASIS Simulation"):
    with st.spinner("Simulating PEGASIS..."):
        alive, energy = simulate_pegasis()
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))
    axs[0].plot(alive)
    axs[0].set_title("Alive Nodes")
    axs[1].plot(energy, color='orange')
    axs[1].set_title("Total Energy")
    for ax in axs: ax.set_xlabel("Round")
    st.pyplot(fig)
    plt.close(fig)
