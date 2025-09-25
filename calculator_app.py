import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Electric vs Diesel HGV Calculator | Net Zero Logistics AI",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Net Zero Logistics AI branding
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0a4f3c 0%, #14b679 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .result-card {
        background: #f8fffe;
        border: 2px solid #e0f2e9;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .winner-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-color: #14b679;
    }
    
    .savings-banner {
        background: linear-gradient(135deg, #14b679 0%, #22d88f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .savings-banner h2 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    .environmental-section {
        background: #e6fffa;
        border: 2px solid #4fd1c5;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .disclaimer {
        background: #f8fafc;
        border-left: 4px solid #e0e0e0;
        padding: 1rem;
        margin: 2rem 0;
        font-size: 0.9rem;
        color: #666;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #14b679 0%, #22d88f 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #22d88f 0%, #14b679 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚛 Electric vs Diesel HGV Calculator</h1>
    <p>Compare total cost of ownership over vehicle lifespan</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for results
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Input sections
st.subheader("⚙️ Vehicle Parameters")
col1, col2 = st.columns(2)

with col1:
    annual_km = st.number_input(
        "Annual Distance (km)", 
        min_value=10000, 
        max_value=500000, 
        value=125000, 
        step=1000,
        help="Average kilometers driven per year"
    )
    
    diesel_efficiency = st.number_input(
        "Diesel Efficiency (km/L)", 
        min_value=1.5, 
        max_value=5.0, 
        value=3.0, 
        step=0.1,
        help="Fuel efficiency for diesel HGV"
    )

with col2:
    vehicle_lifespan = st.number_input(
        "Vehicle Lifespan (years)", 
        min_value=3, 
        max_value=15, 
        value=7, 
        step=1,
        help="Expected operational life of the vehicle"
    )
    
    electric_efficiency = st.number_input(
        "Electric Efficiency (km/kWh)", 
        min_value=0.3, 
        max_value=1.5, 
        value=0.59, 
        step=0.01,
        help="Energy efficiency for electric HGV"
    )

st.subheader("💰 Purchase Costs")
col1, col2 = st.columns(2)

with col1:
    diesel_price = st.number_input(
        "Diesel HGV Price (£)", 
        min_value=50000, 
        max_value=300000, 
        value=120000, 
        step=1000,
        help="Purchase price for diesel HGV"
    )

with col2:
    electric_price = st.number_input(
        "Electric HGV Price (£)", 
        min_value=100000, 
        max_value=500000, 
        value=200000, 
        step=1000,
        help="Purchase price for electric HGV"
    )

st.subheader("🔧 Running Costs")
col1, col2 = st.columns(2)

with col1:
    diesel_fuel_price = st.number_input(
        "Diesel Price (£/L)", 
        min_value=1.0, 
        max_value=3.0, 
        value=1.55, 
        step=0.05,
        help="Current diesel fuel price per litre"
    )
    
    diesel_maintenance = st.number_input(
        "Diesel Maintenance (£/year)", 
        min_value=2000, 
        max_value=20000, 
        value=8000, 
        step=500,
        help="Annual maintenance cost for diesel HGV"
    )

with col2:
    electricity_price = st.number_input(
        "Electricity Price (£/kWh)", 
        min_value=0.10, 
        max_value=0.50, 
        value=0.22, 
        step=0.01,
        help="Electricity cost per kWh"
    )
    
    electric_maintenance = st.number_input(
        "Electric Maintenance (£/year)", 
        min_value=1000, 
        max_value=15000, 
        value=5000, 
        step=500,
        help="Annual maintenance cost for electric HGV"
    )

# Calculate button
if st.button("Calculate Total Costs", type="primary"):
    # Constants for CO2 calculations
    DIESEL_CO2_FACTOR = 2.68  # kg CO2 per litre (RHA standard)
    GRID_CO2_FACTOR = 0.19    # kg CO2 per kWh (UK 2024 average)
    TREE_CO2_ABSORPTION = 21   # kg CO2 per tree per year
    
    # Calculations
    total_km = annual_km * vehicle_lifespan
    
    # Fuel/energy consumption
    diesel_litres = total_km / diesel_efficiency
    electric_kwh = total_km / electric_efficiency
    
    # Costs
    diesel_fuel_cost = diesel_litres * diesel_fuel_price
    electric_energy_cost = electric_kwh * electricity_price
    
    diesel_maintenance_total = diesel_maintenance * vehicle_lifespan
    electric_maintenance_total = electric_maintenance * vehicle_lifespan
    
    diesel_total = diesel_price + diesel_fuel_cost + diesel_maintenance_total
    electric_total = electric_price + electric_energy_cost + electric_maintenance_total
    
    # CO2 calculations
    diesel_co2 = (diesel_litres * DIESEL_CO2_FACTOR) / 1000  # tonnes
    electric_co2 = (electric_kwh * GRID_CO2_FACTOR) / 1000   # tonnes
    co2_saved = diesel_co2 - electric_co2
    co2_reduction_percent = (co2_saved / diesel_co2 * 100) if diesel_co2 > 0 else 0
    annual_co2_saved = co2_saved / vehicle_lifespan
    tree_equivalent = int((co2_saved * 1000) / TREE_CO2_ABSORPTION / vehicle_lifespan)
    
    # Financial calculations
    total_saving = diesel_total - electric_total
    annual_running_cost_diesel = (diesel_fuel_cost + diesel_maintenance_total) / vehicle_lifespan
    annual_running_cost_electric = (electric_energy_cost + electric_maintenance_total) / vehicle_lifespan
    annual_saving = annual_running_cost_diesel - annual_running_cost_electric
    
    upfront_difference = electric_price - diesel_price
    payback_years = upfront_difference / annual_saving if annual_saving > 0 else float('inf')
    
    st.session_state.show_results = True
    
    # Results section
    st.markdown("---")
    
    # Savings banner
    if total_saving > 0:
        st.markdown(f"""
        <div class="savings-banner">
            <h2>Electric HGV saves £{total_saving:,.0f} over {vehicle_lifespan} years</h2>
            <p>Plus {co2_saved:.0f} tonnes CO₂ saved ({co2_reduction_percent:.0f}% reduction)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="savings-banner">
            <h2>Diesel HGV saves £{abs(total_saving):,.0f} over {vehicle_lifespan} years</h2>
            <p>But electric saves {co2_saved:.0f} tonnes CO₂</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cost comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⛽ Diesel HGV")
        st.metric("Total Cost of Ownership", f"£{diesel_total:,.0f}")
        st.markdown("**Cost Breakdown:**")
        st.write(f"- Purchase Price: £{diesel_price:,}")
        st.write(f"- Fuel Costs: £{diesel_fuel_cost:,.0f}")
        st.write(f"- Maintenance: £{diesel_maintenance_total:,.0f}")
        st.write(f"- **Total CO₂:** {diesel_co2:.1f} tonnes")
    
    with col2:
        st.markdown("### ⚡ Electric HGV")
        st.metric("Total Cost of Ownership", f"£{electric_total:,.0f}")
        st.markdown("**Cost Breakdown:**")
        st.write(f"- Purchase Price: £{electric_price:,}")
        st.write(f"- Electricity Costs: £{electric_energy_cost:,.0f}")
        st.write(f"- Maintenance: £{electric_maintenance_total:,.0f}")
        st.write(f"- **Total CO₂:** {electric_co2:.1f} tonnes")
    
    # Annual comparison
    st.markdown("### 📊 Annual Running Cost Comparison")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Diesel Annual", f"£{annual_running_cost_diesel:,.0f}")
    with col2:
        st.metric("Electric Annual", f"£{annual_running_cost_electric:,.0f}")
    with col3:
        st.metric("Annual Saving", f"£{annual_saving:,.0f}")
    with col4:
        if payback_years != float('inf'):
            st.metric("Payback Period", f"{payback_years:.1f} years")
        else:
            st.metric("Payback Period", "N/A")
    
    # Environmental impact
    st.markdown("""
    <div class="environmental-section">
        <h3>🌍 Environmental Impact</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Annual CO₂ Saved", f"{annual_co2_saved:.1f} tonnes")
    with col2:
        st.metric("Lifetime CO₂ Saved", f"{co2_saved:.1f} tonnes")
    with col3:
        st.metric("CO₂ Reduction", f"{co2_reduction_percent:.0f}%")
    with col4:
        st.metric("Equivalent to", f"{tree_equivalent} trees/year")
    
    # Create comparison chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Total Cost Breakdown', 'CO₂ Emissions'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Cost breakdown chart
    fig.add_trace(
        go.Bar(
            x=['Purchase', 'Fuel/Energy', 'Maintenance'],
            y=[diesel_price, diesel_fuel_cost, diesel_maintenance_total],
            name='Diesel',
            marker_color='#ff6b6b',
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=['Purchase', 'Fuel/Energy', 'Maintenance'],
            y=[electric_price, electric_energy_cost, electric_maintenance_total],
            name='Electric',
            marker_color='#14b679',
        ),
        row=1, col=1
    )
    
    # CO2 emissions chart
    fig.add_trace(
        go.Bar(
            x=['Diesel HGV', 'Electric HGV'],
            y=[diesel_co2, electric_co2],
            marker_color=['#ff6b6b', '#14b679'],
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        title_text="Cost and Environmental Comparison",
        barmode='group'
    )
    
    fig.update_xaxes(title_text="Cost Category", row=1, col=1)
    fig.update_yaxes(title_text="Cost (£)", row=1, col=1)
    fig.update_xaxes(title_text="Vehicle Type", row=1, col=2)
    fig.update_yaxes(title_text="CO₂ Emissions (tonnes)", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Carbon note
    st.info(
        "**Carbon calculations:** Based on diesel emissions of 2.68 kg CO₂/L "
        "(Road Haulage Association) and UK grid electricity at 0.19 kg CO₂/kWh (2024 average)."
    )

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <p><strong>Note:</strong> This calculator provides estimates for comparison purposes. 
    Actual costs may vary based on specific vehicle models, routes, and operational factors.</p>
    <p>Want a comprehensive analysis including charging infrastructure and operational impacts? 
    Visit <a href="https://netzerologistics.ai" target="_blank">Net Zero Logistics AI</a> 
    for our full platform.</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>🌱 Powered by "
    "<a href='https://netzerologistics.ai' target='_blank' style='color: #14b679;'>Net Zero Logistics AI</a></p>",
    unsafe_allow_html=True
)
