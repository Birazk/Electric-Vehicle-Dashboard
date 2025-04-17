import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

#Progressbar
st.header("🔄 Calculating EV Energy Consumption...")
progress_bar = st.progress(0)  # Initialize progress bar

for percent in range(100):  
    time.sleep(0.03)  # Simulate calculation time
    progress_bar.progress(percent + 1)

st.success("✅ Calculation Complete!")
st.write("Your estimated range is ???.")


st.title("Energy Consumption Graph")

# Check if P_rr exists in session state
if "P_rr" in st.session_state:
    P_rr = st.session_state["P_rr"]

    # Create a figure
    fig, ax = plt.subplots()
    ax.plot(P_rr, label="Rolling Resistance Power (W)")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Power (W)")
    ax.set_title("Rolling Resistance Power Over Time")
    ax.legend()
    
    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.error("⚠️ No energy data found. Please calculate it first on the main page.")