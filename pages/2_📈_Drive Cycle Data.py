import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium

uploaded_file = st.file_uploader ("Choose a File to Upload", type = "csv")
st.divider()

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    col1, col2= st.columns(2)
    with col1:
        st.subheader("Data Preview") 
        st.write(df.head())
        
    with col2:
        st.subheader("Summary of the Data")
        st.write(df.describe())
        
    st.divider()
    #st.subheader("Filter Data")
    columns = df.columns.tolist()
    selected_columns = st.selectbox("Select the Columns to filter by", columns)
    unique_values = df[selected_columns].unique()
    selected_value = st.selectbox("Select Value", unique_values)
    st.divider()
    st.subheader("Plot Data")
    x_column = st.selectbox("Select the X-axis Column", columns)
    y_column = st.selectbox("Select the Y-axis Column", columns)
    st.divider()

    if "Speed" in df.columns:
        st.session_state['speed_data'] = df["Speed"].tolist()# Save in session_state
        st.success("✅ Speed data saved for processing!")
    else:
        st.error("⚠️ No 'Speed' column found in the uploaded file.")

    if st.button (" Generate Plot "):
        st.line_chart(df.set_index(x_column) [y_column])
else:
    st.write("Waiting fot File Upload")

#import folium
#from streamlit_folium import folium_static

#st.subheader("🗺️ Select Your Driving Route")
#m = folium.Map(location=[37.7749, -122.4194], zoom_start=10)  # Default: San Francisco
#folium.Marker([37.7749, -122.4194], popup="Start").add_to(m)
#folium_static(m)
