import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Constants ---
NUM_NODES = 100
FIELD_X, FIELD_Y = 100, 100
SINK_POS = (50, 150)
INIT_ENERGY = 0.005
E_ELEC = 50 * 1e-9
E_FS = 10 * 1e-12
E_MP = 0.0013 * 1e-12
E_DA = 5 * 1e-9
THRESH_DIST = np.sqrt(E_FS / E_MP)
P_CH = 0.05
ROUNDS = 50

# --- Utility Functions ---
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

# --- LEACH Simulation ---
def simulate_leach():
    nodes = initialize_nodes()
    alive_history, energy_history, ch_history = [], [], []
    plot_area = st.empty()

    for r in range(ROUNDS):
        alive_idx = np.where(nodes['alive'])[0]
        if len(alive_idx) == 0:
            break
        ch_prob = np.random.rand(len(alive_idx))
        ch_idx = alive_idx[ch_prob < P_CH]
        ch_history.append(len(ch_idx))

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, FIELD_X)
        ax.set_ylim(0, FIELD_Y + 60)
        ax.set_title(f"LEACH - Round {r+1}")
        ax.plot(SINK_POS[0], SINK_POS[1], '*k', markersize=12)

        for i in range(NUM_NODES):
            if not nodes['alive'][i]:
                ax.plot(nodes['x'][i], nodes['y'][i], 'ko')
            elif i in ch_idx:
                ax.plot(nodes['x'][i], nodes['y'][i], 'rs')
            else:
                ax.plot(nodes['x'][i], nodes['y'][i], 'bo')

        for i in alive_idx:
            if i in ch_idx:
                d = distance(nodes['x'][i], nodes['y'][i], *SINK_POS)
                e = transmit_energy(4000, d) + E_DA * 4000
                nodes['energy'][i] -= e
                ax.plot([nodes['x'][i], SINK_POS[0]], [nodes['y'][i], SINK_POS[1]], 'g--', lw=0.5)
            else:
                if len(ch_idx) == 0: continue
                dists = distance(nodes['x'][i], nodes['y'][i], nodes['x'][ch_idx], nodes['y'][ch_idx])
                ch_id = ch_idx[np.argmin(dists)]
                dist = dists.min()
                nodes['energy'][i] -= transmit_energy(4000, dist)
                nodes['energy'][ch_id] -= receive_energy(4000)
                ax.plot([nodes['x'][i], nodes['x'][ch_id]], [nodes['y'][i], nodes['y'][ch_id]], 'y-', lw=0.3)

        nodes['alive'] = nodes['energy'] > 0
        alive_history.append(np.sum(nodes['alive']))
        energy_history.append(np.sum(nodes['energy'][nodes['alive']]))
        plot_area.pyplot(fig)
        plt.close(fig)
        time.sleep(0.4)

    return alive_history, energy_history, ch_history

# --- Streamlit UI ---

st.title("Wireless Sensor Network Routing Protocol Simulator")

st.markdown("""
Explore the behavior of four energy-efficient routing protocols:
- **LEACH** (Cluster-based)
- **PEGASIS** (Chain-based)
- **Directed Diffusion** (Data-centric)
- **GEAR** (Geographic routing)

Each protocol is animated and tracks energy, alive nodes, and CHs.
""")

tabs = st.tabs(["LEACH", "PEGASIS", "Directed Diffusion", "GEAR"])

with tabs[0]:
    st.subheader("LEACH Protocol Simulation")
    if st.button("Run LEACH Simulation"):
        with st.spinner("Simulating LEACH..."):
            alive, energy, ch = simulate_leach()
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

with tabs[1]:
    st.subheader("PEGASIS Protocol Simulation")
    st.info("PEGASIS simulation coming soon... 🚧")

with tabs[2]:
    st.subheader("Directed Diffusion Protocol Simulation")
    st.info("Directed Diffusion simulation coming soon... 🚧")

with tabs[3]:
    st.subheader("GEAR Protocol Simulation")
    st.info("GEAR simulation coming soon... 🚧")
