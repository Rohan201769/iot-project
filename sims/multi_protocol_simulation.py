import streamlit as st
st.set_page_config(layout="centered")
from leach_sim import simulate_leach
from pegasis_sim import simulate_pegasis
from gear_sim import simulate_gear
from diffusion_sim import simulate_directed_diffusion
import matplotlib.pyplot as plt

# Streamlit UI Setup

st.title("Routing Protocol Simulations")

# Create tabs for each protocol
protocol = st.selectbox("Select Routing Protocol", ["LEACH", "PEGASIS", "GEAR", "Directed Diffusion"])

# Show corresponding protocol simulation
if protocol == "LEACH":
    st.header("LEACH Protocol Simulation")
    if st.button("Run LEACH Simulation", key="leach"):
        with st.spinner("Simulating LEACH..."):
            alive, energy, ch = simulate_leach()
        fig, axs = plt.subplots(2, 1, figsize=(10, 6))
        axs[0].plot(alive)
        axs[0].set_title("Alive Nodes")
        axs[1].plot(energy, color='orange')
        axs[1].set_title("Total Energy")
        for ax in axs: ax.set_xlabel("Round")
        st.pyplot(fig)
        plt.close(fig)


elif protocol == "PEGASIS":
    st.header("PEGASIS Protocol Simulation", key="pegasis")
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

elif protocol == "GEAR":
    st.header("GEAR Protocol Simulation", kye='gear')
    if st.button("Run GEAR Simulation"):
        with st.spinner("Simulating GEAR..."):
            alive, energy = simulate_gear()
        fig, axs = plt.subplots(2, 1, figsize=(10, 6))
        axs[0].plot(alive)
        axs[0].set_title("Alive Nodes")
        axs[1].plot(energy, color='orange')
        axs[1].set_title("Total Energy")
        for ax in axs: ax.set_xlabel("Round")
        st.pyplot(fig)
        plt.close(fig)

elif protocol == "Directed Diffusion":
    st.header("Directed Diffusion Protocol Simulation")
    if st.button("Run Directed Diffusion Simulation", key='directedDiffusion'):
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