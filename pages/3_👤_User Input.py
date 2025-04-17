import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Constants
RHO = 1.225        # Air density (kg/m³)
G = 9.81           # Gravity (m/s²)
DT = 1             # Time step (s)

# Efficiencies
ETA_BATT = 0.9
ETA_MOTOR = 0.95
ETA_TRANS = 0.9  # Transmission efficiency
ETA_REGEN = 0.3  # Regenerative braking efficiency

# ---- Load Speed Data ----
st.title("🚗 Enhanced EV Range & Cost Calculator")
st.divider()

if "speed_data" in st.session_state:
    speed_data = np.array(st.session_state["speed_data"])
    st.success("✅ Speed Data Loaded Successfully!")
    st.line_chart(speed_data)
else:
    st.error("⚠️ No speed data found. Please upload a Drive Cycle file first.")
    st.stop()

# ---- Vehicle & Drive Parameters ----
st.header("🔧 Vehicle & Environmental Parameters")
if "A" in st.session_state:
    A = st.session_state["A"]  # Frontal area (m²)
    st.write(f"Frontal Area: {A} m²")
else:
    st.warning("No frontal area found. Please go back and enter values first.")

with st.form(key="vehicle_form"):
    m = st.number_input("🚙 Vehicle Mass (kg)", min_value=1.0, value=800.0)
    Cr = st.number_input("🛞 Rolling Resistance Coefficient", min_value=0.001, value=0.02, help = " for a car tire on a smooth asphalt or concrete road is between 0.007 and 0.02")
    Cd = st.number_input("💨 Drag Coefficient", min_value=0.1, value=0.3)
    grade = st.slider("🏔️ Road Gradient (%)", min_value=0, max_value=30, value=5)
    B_capacity = st.number_input("🔋 Battery Capacity (kWh)", min_value=1.0, value=7.5)
    V_nom = st.number_input("⚡ Battery Nominal Voltage (V)", min_value=1.0, value=72.0)
    soc_initial = st.slider("🔋 Initial State of Charge (%)", min_value=0, max_value=100, value=50)
    st.form_submit_button("Submit Vehicle Parameters")

# ---- Additional Modeling Factors for EV ----
st.header("🔍 Additional Modeling Factors")
with st.form(key="refined_params"):
    usable_fraction = st.slider("Available Battery Fraction (%)", min_value=50, max_value=100, value=80,
                                  help="The portion of battery capacity actually usable (e.g., 80%).")
    battery_health = st.slider("Battery Health Factor (%)", min_value=50, max_value=100, value=100,
                               help="100% for a new battery; lower values indicate degradation.")
    ambient_temp = st.slider("Ambient Temperature (°C)", min_value=-10, max_value=40, value=20,
                             help="Battery performance can degrade in extreme temperatures.")
    st.form_submit_button("Submit Refined Parameters")

# ---- Cost Analysis Inputs ----
st.header("💡 Range and Cost Analysis Inputs")
with st.form(key="cost_form"):
    # Auxiliary load (W) can be applied to the EV.
    P_aux = st.number_input("🔌 Auxiliary Load (W)", min_value=0, value=1000,
                            help="Constant auxiliary power draw (e.g., HVAC).")
    elec_price = st.number_input("💰 Electricity Price (per kWh)", min_value=0.01, value=0.7,
                                  help = "70 paisa per kilometer for cars, 80 paisa per kilometer for SUVs, 90 paisa per kilometer for microbuses, and 120 paisa per kilometer for buses")
    # Petrol vehicle parameters:
    fuel_economy = st.number_input("⛽ Petrol Fuel Economy (L/100km)", min_value=0.1, value=8.0,
                                   help="Petrol consumption in L/100km.")
    fuel_price = st.number_input("💲 Petrol Price (per Liter)", min_value=100, value=165)
    st.form_submit_button("Submit Cost Parameters")

st.divider()

# ---- Energy Calculations ----
st.header("⚙️ Energy Consumption Calculations")

def calculate_rolling_resistance(m, Cr, speed):
    F_rolling = m * G * Cr  # (N)
    P_rr = F_rolling * speed  # (W)
    E_rr_Wh = np.sum(P_rr * DT) / 3600.0  # (Wh)
    return F_rolling, P_rr, E_rr_Wh

def calculate_aero_drag(Cd, A, speed):
    F_aero = 0.5 * Cd * A * RHO * speed**2
    P_aero = F_aero * speed  # (W)
    E_aero_Wh = np.sum(P_aero * DT) / 3600.0
    return F_aero, P_aero, E_aero_Wh

def calculate_kinetic_energy(m, speed):
    KE = 0.5 * m * speed**2  # (J)
    E_acc_Wh = np.sum(np.maximum(KE, 0)) / 3600.0
    return KE, E_acc_Wh

def calculate_potential_energy(m, grade, speed):
    d_x = speed * DT  # Horizontal distance (m)
    d_h = d_x * np.sin(np.deg2rad(grade))
    dPE = m * G * d_h  # (J)
    E_PE_Wh = np.sum(np.maximum(dPE, 0)) / 3600.0
    return dPE, E_PE_Wh

F_rolling, P_rr, E_rr_Wh = calculate_rolling_resistance(m, Cr, speed_data)
F_aero, P_aero, E_aero_Wh = calculate_aero_drag(Cd, A, speed_data)
KE, E_acc_Wh = calculate_kinetic_energy(m, speed_data)
dPE, E_PE_Wh = calculate_potential_energy(m, grade, speed_data)

# Total mechanical energy at the wheels (Wh)
E_mech_Wh = E_rr_Wh + E_aero_Wh + E_acc_Wh + E_PE_Wh
# Adjust for transmission losses
E_battery_required_Wh = E_mech_Wh / (ETA_TRANS * ETA_MOTOR * ETA_BATT)

# Total Mechanical Energy at Wheels
E_mech_Wh = E_rr_Wh + E_aero_Wh + E_acc_Wh + E_PE_Wh
E_battery_required_Wh = E_mech_Wh / ETA_TRANS
E_trans_loss_Wh = E_battery_required_Wh - E_mech_Wh

# Regenerative Braking Energy Recovery
E_regen_J = np.sum((np.abs(np.minimum(KE, 0))) * ETA_REGEN)
E_regen_Wh = E_regen_J / 3600.0

# Nominal battery energy in Wh (before adjustments)
E_nominal = B_capacity * 1000

# ---- Refined Battery Energy Model ----
# Usable battery energy is less than the nominal capacity:
#  - usable_fraction is a percentage (e.g., 80% of nominal capacity)
#  - battery_health accounts for degradation (100% for new, lower otherwise)
#  - Temperature effects: Here we use a simplistic model where very low or high temperatures reduce efficiency.
if ambient_temp < 15:
    temp_efficiency = 0.9  # Cold weather penalty
elif ambient_temp > 30:
    temp_efficiency = 0.95  # Slight penalty in very hot conditions
else:
    temp_efficiency = 1.0

usable_capacity_Wh = E_nominal * (usable_fraction / 100.0) * (battery_health / 100.0) * temp_efficiency



# ---- Display Results ----
st.header("🔋 Energy Consumption Breakdown")

# Dictionary to store energy components
energy_data = {
    "Rolling Resistance": E_rr_Wh,
    "Aerodynamic Drag": E_aero_Wh,
    "Kinetic Energy (Acceleration)": E_acc_Wh,
    "Potential Energy (Uphill)": E_PE_Wh,
    "Transmission Losses": E_trans_loss_Wh,
    "Regenerative Braking (Recovered)": -E_regen_Wh,  # Negative for visualization
}

# Enhanced Donut Chart for Energy Breakdown
fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    list(energy_data.values()),
    labels=list(energy_data.keys()),
    autopct='%1.1f%%',
    startangle=180,
    pctdistance=0.85,  # Position of percentage labels
    wedgeprops=dict(width=0.4, edgecolor='w')
)

# Draw center circle for donut effect
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

# Improve the text size and style
plt.setp(autotexts, size=10, weight="bold", color="navy")
plt.setp(texts, size=12)

ax.set_title("🔋 Energy Distribution (Wh)", fontsize=16)
ax.axis('equal')  # Ensures that the pie is drawn as a circle

st.pyplot(fig)

# **Energy Summary Table**
st.write("#### ✅ Key Energy Metrics")
st.markdown(f"""
- **Total Mechanical Energy:** `{E_mech_Wh:.2f}` Wh  
- **Battery Energy Required:** `{E_battery_required_Wh:.2f}` Wh  
- **Nominal Battery Energy:** `{E_nominal:.2f}` Wh  
""")

# **Progress bar for battery usage**
battery_usage = E_battery_required_Wh / E_nominal
st.progress(min(battery_usage, 1.0))  # Capped at 100%

# ---- Range Calculations ----
st.header("🚀 Range Estimation")

# Compute drive cycle distance
T_total = len(speed_data) * DT
distance_m = np.sum(speed_data * DT)
distance_km = distance_m / 1000.0

# Energy consumption and range calculations
consumption_normal = E_battery_required_Wh / distance_km
range_normal = usable_capacity_Wh / consumption_normal

E_aux_Wh = (P_aux * T_total) / 3600.0
consumption_aux = (E_battery_required_Wh + E_aux_Wh) / distance_km
range_aux = usable_capacity_Wh / consumption_aux

# **Range comparison bars**
st.metric(label="🚗 Estimated Range (Normal)", value=f"{range_normal:.2f} km")
st.metric(label="⚡ Range with Auxiliary Load", value=f"{range_aux:.2f} km")

st.progress(min(range_normal / 500, 1.0))  # Assuming 500km max range visualization

# ---- Cost Analysis ----
st.header("💲 Cost Comparison: EV vs. Petrol")

# EV and petrol cost per km
ev_cost_normal = (consumption_normal / 1000.0) * elec_price
ev_cost_aux = (consumption_aux / 1000.0) * elec_price
petrol_cost_per_km = (fuel_economy / 100.0) * fuel_price

# **Bar chart for cost per km**
cost_labels = ["EV (Normal)", "EV (With Aux)", "Petrol"]
cost_values = [ev_cost_normal, ev_cost_aux, petrol_cost_per_km]

fig, ax = plt.subplots()
ax.bar(cost_labels, cost_values, color=["green", "blue", "red"])
ax.set_ylabel("Cost per km (Rs)")
ax.set_title("💰 Cost Comparison: EV vs Petrol")
st.pyplot(fig)

# **Savings Calculation**
saving_normal = petrol_cost_per_km - ev_cost_normal
saving_aux = petrol_cost_per_km - ev_cost_aux
total_savings_normal = saving_normal * range_normal
total_savings_aux = saving_aux * range_aux

st.write("#### 🔍 Savings Overview")
st.markdown(f"""
- **💵 Savings per km (Normal EV):** `{saving_normal:.3f} Rs`  
- **💵 Savings per km (EV with Aux):** `{saving_aux:.3f} Rs`  
- **💰 Total Savings (Normal Range):** `{total_savings_normal:.2f} Rs`  
- **💰 Total Savings (With Aux):** `{total_savings_aux:.2f} Rs`  
""")

# ---- Store Results ----
st.session_state["E_mech_Wh"] = E_mech_Wh
st.session_state["E_battery_required_Wh"] = E_battery_required_Wh
st.success("✅ Data stored! Visit 'THE MATRIX' page for advanced visualization.")


