import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Set Page Title & Icon
st.set_page_config(page_title="EV Energy & Range Calculator", page_icon="⚡")

st.title (" Electric Vehicle Dashboard")
st.header("Energy Consumption and Range Detection")
st.divider()

# Introduction Section
st.markdown("""
# **Welcome to the EV Energy & Range Calculator** ⚡🚗  
Are you curious about how far your electric vehicle (EV) can go on a full charge?  
Or how different driving conditions affect energy consumption?  
This tool helps you estimate the **energy efficiency and range** of your EV based on real-world factors.  

## **🔍 What This Website Does:**  
✅ Calculates **energy consumption (Wh/km or Wh/mile)** based on vehicle specs and driving conditions.  
✅ Estimates **driving range** based on your EV’s battery capacity.  
✅ Visualizes **energy losses** from aerodynamics, rolling resistance, and terrain.  
✅ Helps optimize your driving habits to **maximize efficiency and range**.  

## **🚀 Get Started**  
1️⃣ **Enter your vehicle details and driving conditions** in the sidebar Vehicle Dynamics (Drag, Rolling Resistance, Kinetic Energy).  
2️⃣ **View real-time energy consumption & range estimates** in the main display.  
3️⃣ **Analyze interactive charts and insights** to optimize your driving.  

⚠️ *Note: This tool provides estimates based on input values. Actual results may vary due to environmental and operational factors.*  

---
""", unsafe_allow_html=True)
st.divider()

st.header("Please Enter Your Information for Further Processing.")
name = st.text_input("Enter the name of the Vehicle")

st.subheader("Enter the Dimensions of the vehicle")
col1, col2, col3 = st.columns(3)
with col1:
    L = st.number_input("Enter the Lenght (mm)")

with col2:
     B = st.number_input("Enter the Breadth (mm)")

with col3:
     H = st.number_input("Enter the Height (mm)")    

Frontal_area = (0.85 * B * H)
frontal_area = Frontal_area / 1000000

# Save to session state
if st.button("Save Data"):
    st.session_state["A"] = frontal_area
    st.success("Data saved successfully!")

# Optional: Add a Call-to-Action Button
if st.button("Start Calculation 🚀"):
    st.sidebar.success("Enter your vehicle details to begin!")