# 1bhk=> 2-light*.4kv ,2-fans*8kv ,1-washing mahine*2kv ,fridge*4kv, 2-ac*3kv
# 2bhk=> 3-light ,3-fans ,1-washing mahine,fridge, 3-ac
# 3bhk=> 4-light ,4-fans ,1-washing mahine,fridge, 4-ac
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="⚡ ElectriTrack - Smart Energy Monitor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            
    }
    
    .appliance-card {
        color:black;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        
    }
    
    .usage-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #white;
    }
    
    .stNumberInput > div > div {
        background-color: #white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'usage_history' not in st.session_state:
    st.session_state.usage_history = []

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ ElectriTrack - Smart Energy Monitor</h1>
    <p>Track, Analyze & Optimize Your Home's Electricity Consumption</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for user information
st.sidebar.markdown("## 👤 User Information")
with st.sidebar.expander("Personal Details", expanded=True):
    name = st.text_input("Full Name", placeholder="Enter your name")
    age = st.number_input("Age", min_value=18, max_value=100, value=25)
    city = st.text_input("City", placeholder="Enter your city")
    area = st.text_input("Area/Locality", placeholder="Enter your area")
    house_type = st.selectbox("House Type", ["Flat", "Tenement", "Independent House"])

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🏠 Home Configuration")
    
    # BHK Selection with visual cards
    bhk_options = {
        "1 BHK": {"lights": 2, "fans": 2, "base_load": 1.2},
        "2 BHK": {"lights": 3, "fans": 3, "base_load": 1.8},
        "3 BHK": {"lights": 4, "fans": 4, "base_load": 2.4}
    }
    
    selected_bhk = st.selectbox("Select BHK Type", list(bhk_options.keys()))
    
    # Display default appliances for selected BHK
    st.markdown(f"### Default Configuration for {selected_bhk}")
    config = bhk_options[selected_bhk]
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div class="appliance-card">
            <h4>💡 Lights</h4>
            <p>{config['lights']} units @ 0.4kW each</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <div class="appliance-card">
            <h4>🌀 Fans</h4>
            <p>{config['fans']} units @ 0.8kW each</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_c:
        st.markdown(f"""
        <div class="appliance-card">
            <h4>🔌 Base Load</h4>
            <p>{config['base_load']} kW</p>
        </div>
        """, unsafe_allow_html=True)

    # Additional appliances
    st.markdown("### Additional Appliances")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        washing_machine = st.checkbox("🧺 Washing Machine (2kW)")
        fridge = st.checkbox("🧊 Refrigerator (4kW)")
        
    with col_y:
        has_ac = st.checkbox("❄️ Air Conditioner")
        if has_ac:
            ac_count = st.number_input("Number of ACs", min_value=1, max_value=10, value=1)
            ac_power = st.slider("AC Power (kW each)", 1.0, 5.0, 3.0, 0.5)
        else:
            ac_count = 0
            ac_power = 0

    # Usage hours
    st.markdown("### ⏰ Daily Usage Hours")
    col_h1, col_h2, col_h3 = st.columns(3)
    
    with col_h1:
        light_hours = st.slider("Lights (hours/day)", 0, 24, 8)
        fan_hours = st.slider("Fans (hours/day)", 0, 24, 12)
    
    with col_h2:
        if washing_machine:
            wm_hours = st.slider("Washing Machine (hours/day)", 0, 8, 1)
        else:
            wm_hours = 0
            
        if fridge:
            fridge_hours = st.slider("Refrigerator (hours/day)", 0, 24, 24)
        else:
            fridge_hours = 0
    
    with col_h3:
        if has_ac:
            ac_hours = st.slider("AC (hours/day)", 0, 24, 8)
        else:
            ac_hours = 0

# Calculate energy consumption
def calculate_energy(bhk_type, wm, fridge_on, ac_num, ac_pow, 
                    light_h, fan_h, wm_h, fridge_h, ac_h):
    config = bhk_options[bhk_type]
    
    # Daily consumption in kWh
    daily_consumption = (
        config['lights'] * 0.4 * light_h +  # Lights
        config['fans'] * 0.8 * fan_h +      # Fans
        (2.0 * wm_h if wm else 0) +         # Washing machine
        (4.0 * fridge_h if fridge_on else 0) +  # Fridge
        (ac_num * ac_pow * ac_h)            # ACs
    )
    
    return daily_consumption

# Calculate current consumption
daily_kwh = calculate_energy(selected_bhk, washing_machine, fridge, ac_count, ac_power,
                            light_hours, fan_hours, wm_hours, fridge_hours, ac_hours)

# Right column - Results and Analytics
with col2:
    st.markdown("## 📊 Energy Analytics")
    
    # Current consumption metrics
    weekly_kwh = daily_kwh * 7
    monthly_kwh = daily_kwh * 30
    
    # Assuming electricity rate (₹/kWh)
    rate_per_kwh = st.number_input("Electricity Rate (₹/kWh)", 
                                   min_value=1.0, max_value=20.0, value=6.5, step=0.5)
    
    daily_cost = daily_kwh * rate_per_kwh
    weekly_cost = weekly_kwh * rate_per_kwh
    monthly_cost = monthly_kwh * rate_per_kwh
    
    # Display metrics
    st.markdown(f"""
    <div class="usage-stats">
        <h3>⚡ Current Usage</h3>
        <h2>{daily_kwh:.2f} kWh/day</h2>
        <p>₹{daily_cost:.2f} per day</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics display
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.metric("📅 Weekly", f"{weekly_kwh:.1f} kWh", f"₹{weekly_cost:.0f}")
        st.metric("🏠 Monthly", f"{monthly_kwh:.1f} kWh", f"₹{monthly_cost:.0f}")
    
    with col_m2:
        co2_emissions = daily_kwh * 0.82  # kg CO2 per kWh (India average)
        st.metric("🌱 Daily CO₂", f"{co2_emissions:.1f} kg")
        st.metric("🔋 Efficiency", "Good" if daily_kwh < 15 else "High")

# Save current reading
if st.button("💾 Save Current Reading", type="primary"):
    if name:
        reading = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'name': name,
            'bhk': selected_bhk,
            'daily_kwh': daily_kwh,
            'daily_cost': daily_cost,
            'appliances': {
                'lights': config['lights'],
                'fans': config['fans'],
                'washing_machine': washing_machine,
                'fridge': fridge,
                'ac_count': ac_count
            }
        }
        st.session_state.usage_history.append(reading)
        st.success("✅ Reading saved successfully!")
    else:
        st.error("Please enter your name first!")

# Historical data and charts
if st.session_state.usage_history:
    st.markdown("## 📈 Usage History & Trends")
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.usage_history)
    df['date'] = pd.to_datetime(df['date'])
    
    # Charts
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Daily consumption trend
        fig_trend = px.line(df, x='date', y='daily_kwh', 
                           title='Daily Energy Consumption Trend',
                           labels={'daily_kwh': 'Energy (kWh)', 'date': 'Date'})
        fig_trend.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_c2:
        # Cost analysis
        fig_cost = px.bar(df, x='date', y='daily_cost',
                         title='Daily Electricity Cost',
                         labels={'daily_cost': 'Cost (₹)', 'date': 'Date'})
        fig_cost.update_traces(marker_color='#764ba2')
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Summary statistics
    st.markdown("### 📊 Summary Statistics")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric("Average Daily", f"{df['daily_kwh'].mean():.1f} kWh")
    with col_s2:
        st.metric("Highest Usage", f"{df['daily_kwh'].max():.1f} kWh")
    with col_s3:
        st.metric("Lowest Usage", f"{df['daily_kwh'].min():.1f} kWh")
    with col_s4:
        st.metric("Total Records", len(df))

# Appliance breakdown
st.markdown("## 🔌 Current Appliance Breakdown")

# Calculate individual appliance consumption
appliance_data = []
if config['lights'] > 0:
    appliance_data.append({'Appliance': 'Lights', 'Power (kW)': config['lights'] * 0.4, 
                          'Hours': light_hours, 'Daily kWh': config['lights'] * 0.4 * light_hours})
if config['fans'] > 0:
    appliance_data.append({'Appliance': 'Fans', 'Power (kW)': config['fans'] * 0.8, 
                          'Hours': fan_hours, 'Daily kWh': config['fans'] * 0.8 * fan_hours})
if washing_machine:
    appliance_data.append({'Appliance': 'Washing Machine', 'Power (kW)': 2.0, 
                          'Hours': wm_hours, 'Daily kWh': 2.0 * wm_hours})
if fridge:
    appliance_data.append({'Appliance': 'Refrigerator', 'Power (kW)': 4.0, 
                          'Hours': fridge_hours, 'Daily kWh': 4.0 * fridge_hours})
if has_ac:
    appliance_data.append({'Appliance': f'AC ({ac_count} units)', 'Power (kW)': ac_count * ac_power, 
                          'Hours': ac_hours, 'Daily kWh': ac_count * ac_power * ac_hours})

if appliance_data:
    appliance_df = pd.DataFrame(appliance_data)
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.dataframe(appliance_df, use_container_width=True, hide_index=True)
    
    with col_t2:
        # Pie chart for appliance consumption
        fig_pie = px.pie(appliance_df, values='Daily kWh', names='Appliance',
                        title='Energy Consumption by Appliance')
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

# Tips and recommendations
st.markdown("## 💡 Energy Saving Tips")
tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    ### 🌟 Quick Tips
    - Switch to LED lights (75% energy savings)
    - Use ceiling fans instead of AC when possible
    - Set AC temperature to 24°C or higher
    - Unplug devices when not in use
    - Use natural light during daytime
    """)

with tips_col2:
    st.markdown("""
    ### 📱 Smart Usage
    - Run washing machine with full loads
    - Clean AC filters regularly
    - Use timer settings on appliances
    - Consider solar panels for long-term savings
    - Monitor peak hour usage
    """)

# Footer
st.markdown("---")
st.markdown("*ElectriTrack - Making homes more energy efficient, one kilowatt at a time! 🌱*")
st.markdown("BY RIYA SHAH")