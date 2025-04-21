# multi_protocol_simulation.py
import streamlit as st
st.set_page_config(layout="centered")
from leach_sim import simulate_leach
from pegasis_sim import simulate_pegasis
from gear_sim import simulate_gear
from diffusion_sim import simulate_directed_diffusion
from config import get_simulation_parameters
import matplotlib.pyplot as plt
import numpy as np

# Streamlit UI Setup
st.title("Routing Protocol Simulations")

# Get common configuration
config = get_simulation_parameters()

# Create tabs for each protocol
protocol = st.selectbox("Select Routing Protocol", ["LEACH", "PEGASIS", "GEAR", "Directed Diffusion"])

# Protocol-specific parameters
if protocol == "LEACH":
    with st.sidebar.expander("LEACH Parameters", expanded=True):
        config['P_CH'] = st.slider("Cluster Head Probability", 0.01, 0.2, 0.05, step=0.01)

elif protocol == "PEGASIS":
    # No additional parameters for PEGASIS
    pass

elif protocol == "GEAR":
    with st.sidebar.expander("GEAR Parameters", expanded=True):
        config['COMM_RANGE'] = st.slider("Communication Range", 10, 50, 30)

elif protocol == "Directed Diffusion":
    with st.sidebar.expander("Directed Diffusion Parameters", expanded=True):
        config['INTEREST_DURATION'] = st.slider("Interest Duration (rounds)", 1, 20, 10)
        config['INTEREST_NODES'] = st.slider("Number of Interest Nodes", 1, 20, 5)

# Display comparison
if st.checkbox("Compare with Previous Run"):
    st.info("Run a simulation first to enable comparison with previous run")

# Run simulation button
if st.button(f"Run {protocol} Simulation"):
    with st.spinner(f"Simulating {protocol}..."):
        if protocol == "LEACH":
            alive, energy, ch = simulate_leach(config)
            
            fig, axs = plt.subplots(3, 1, figsize=(10, 12))
            axs[0].plot(alive)
            axs[0].set_title("Alive Nodes")
            axs[1].plot(energy, color='orange')
            axs[1].set_title("Total Energy")
            axs[2].plot(ch, color='green')
            axs[2].set_title("CHs per Round")
            
        elif protocol == "PEGASIS":
            alive, energy = simulate_pegasis(config)
            
            fig, axs = plt.subplots(2, 1, figsize=(10, 8))
            axs[0].plot(alive)
            axs[0].set_title("Alive Nodes")
            axs[1].plot(energy, color='orange')
            axs[1].set_title("Total Energy")
            
        elif protocol == "GEAR":
            alive, energy = simulate_gear(config)
            
            fig, axs = plt.subplots(2, 1, figsize=(10, 8))
            axs[0].plot(alive)
            axs[0].set_title("Alive Nodes")
            axs[1].plot(energy, color='orange')
            axs[1].set_title("Total Energy")
            
        elif protocol == "Directed Diffusion":
            alive, energy = simulate_directed_diffusion(config)
            
            fig, axs = plt.subplots(2, 1, figsize=(10, 8))
            axs[0].plot(alive)
            axs[0].set_title("Alive Nodes")
            axs[1].plot(energy, color='orange')
            axs[1].set_title("Total Energy")
        
        # Common formatting for all plots
        for ax in axs:
            ax.set_xlabel("Round")
            ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close(fig)
        
        # Save results for comparison
        if 'previous_results' not in st.session_state:
            st.session_state.previous_results = {}
        
        st.session_state.previous_results[protocol] = {
            'alive': alive,
            'energy': energy,
            'config': config.copy()
        }
        
        # Display summary statistics
        st.write("### Simulation Results")
        
        # Calculate key metrics
        first_dead = next((i for i, a in enumerate(alive) if a < config['NUM_NODES']), len(alive))
        half_dead = next((i for i, a in enumerate(alive) if a <= config['NUM_NODES']/2), len(alive))
        network_lifetime = len(alive)
        
        energy_per_node = energy[-1]/config['NUM_NODES'] if len(energy) > 0 else 0
        metrics_df = pd.concat([metrics_df, pd.DataFrame({
            "Metric": ["Final Energy Level (per node)"],
            "Value": [energy_per_node]
        })])

        
        st.table(metrics_df)

# Add algorithm descriptions
with st.expander("Protocol Descriptions"):
    st.markdown("""
    ### LEACH (Low-Energy Adaptive Clustering Hierarchy)
    LEACH is a hierarchical protocol where nodes organize themselves into clusters. 
    Each cluster has a cluster head (CH) that aggregates data from all cluster members 
    and sends it to the sink. The role of CH rotates to balance energy consumption.
    
    ### PEGASIS (Power-Efficient GAthering in Sensor Information Systems)
    PEGASIS forms a chain of sensor nodes so that each node transmits to and receives 
    from only close neighbors. A leader node is selected in each round to transmit the 
    aggregated data to the sink.
    
    ### GEAR (Geographic and Energy Aware Routing)
    GEAR uses geographic information and remaining energy levels to route data. It divides 
    the network into regions and selects forwarding paths based on energy-distance metrics.
    
    ### Directed Diffusion
    Directed Diffusion is a data-centric protocol where the sink broadcasts interests for 
    named data. Gradients are established to draw events matching these interests, and paths 
    are reinforced based on data delivery performance.
    """)