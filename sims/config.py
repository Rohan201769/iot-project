# config.py
import streamlit as st

def get_simulation_parameters():
    """Get common simulation parameters with UI controls"""
    
    with st.sidebar.expander("Simulation Parameters", expanded=True):
        num_nodes = st.slider("Number of Nodes", 20, 200, 100)
        rounds = st.slider("Number of Rounds", 10, 200, 50)
        init_energy = st.slider("Initial Energy", 0.001, 1.0, 0.5, step=0.001, 
                              format="%.3f", help="Higher values = longer node lifetime")
        packet_size = st.select_slider("Packet Size (bits)", 
                                     options=[1000, 2000, 4000, 8000, 16000], 
                                     value=4000)
        
        # Energy model parameters
        st.write("Energy Model Parameters:")
        e_elec = st.slider("Electronics Energy (E_ELEC)", 1e-9, 100e-9, 50e-9, format="%.1e")
        e_fs = st.slider("Free Space Amp Energy (E_FS)", 1e-12, 50e-12, 10e-12, format="%.1e")
        e_mp = st.slider("Multi-Path Amp Energy (E_MP)", 0.0001e-12, 0.01e-12, 0.0013e-12, format="%.5e")
        e_da = st.slider("Data Aggregation Energy (E_DA)", 1e-9, 20e-9, 5e-9, format="%.1e")
    
    # Calculate threshold distance
    thresh_dist = (e_fs / e_mp)**0.5
    
    return {
        'NUM_NODES': num_nodes,
        'FIELD_X': 100,
        'FIELD_Y': 100,
        'SINK_POS': (50, 150),
        'INIT_ENERGY': init_energy,
        'ROUNDS': rounds,
        'PACKET_SIZE': packet_size,
        'THRESH_DIST': thresh_dist,
        'E_ELEC': e_elec,
        'E_FS': e_fs,
        'E_MP': e_mp,
        'E_DA': e_da
    }