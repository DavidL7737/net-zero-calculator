#!/usr/bin/env python3
"""
HGV/Van Electric vs Diesel Calculator - Streamlit Application
"""

import streamlit as st
import pandas as pd
import csv
import os
from datetime import datetime
import json

# Configure Streamlit page
st.set_page_config(
    page_title="HGV/Van Electric vs Diesel Calculator",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Vehicle data configuration
VEHICLE_DATA = {
    "van_small": {
        "name": "Small Van (up to 2.5t)",
        "electric_price": 35000,
        "diesel_price": 25000,
        "electric_efficiency": 3.5,  # kWh/mile
        "diesel_efficiency": 35,  # mpg
        "default_mileage": 15000,
        "grant": 2500,
        "test_frequency": "Annual MOT after 3 years",
        "assumptions": [
            "Electric vehicle price decreasing 8% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.35/kWh commercial rate (Ofgem, 2024)",
            "Diesel cost: £1.45/litre average commercial rate (DfT, 2024)",
            "Van grants available up to £2,500 (OZEV, 2024)",
            "Insurance premium 15% higher for electric (SMMT, 2024)",
            "Maintenance costs 40% lower for electric (Logistics UK, 2024)"
        ]
    },
    "van_medium": {
        "name": "Medium Van (2.5-3.5t)",
        "electric_price": 45000,
        "diesel_price": 30000,
        "electric_efficiency": 4.2,
        "diesel_efficiency": 32,
        "default_mileage": 20000,
        "grant": 2500,
        "test_frequency": "Annual MOT after 3 years",
        "assumptions": [
            "Electric vehicle price decreasing 8% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.35/kWh commercial rate (Ofgem, 2024)",
            "Diesel cost: £1.45/litre average commercial rate (DfT, 2024)",
            "Van grants available up to £2,500 (OZEV, 2024)",
            "Insurance premium 15% higher for electric (SMMT, 2024)",
            "Maintenance costs 40% lower for electric (Logistics UK, 2024)"
        ]
    },
    "van_large": {
        "name": "Large Van (3.5-7.5t)",
        "electric_price": 65000,
        "diesel_price": 45000,
        "electric_efficiency": 5.8,
        "diesel_efficiency": 28,
        "default_mileage": 25000,
        "grant": 9000,
        "test_frequency": "Annual MOT from first use",
        "assumptions": [
            "Electric vehicle price decreasing 10% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.32/kWh commercial rate (Ofgem, 2024)",
            "Diesel cost: £1.45/litre average commercial rate (DfT, 2024)",
            "Large van grants available up to £9,000 (OZEV, 2024)",
            "Insurance premium 20% higher for electric (SMMT, 2024)",
            "Maintenance costs 45% lower for electric (Logistics UK, 2024)"
        ]
    },
    "hgv_rigid_small": {
        "name": "Rigid HGV 7.5-12t",
        "electric_price": 120000,
        "diesel_price": 65000,
        "electric_efficiency": 1.8,  # miles/kWh
        "diesel_efficiency": 12,
        "default_mileage": 35000,
        "grant": 25000,
        "test_frequency": "Annual MOT from first use, 6-weekly roadworthiness tests",
        "assumptions": [
            "Electric HGV price decreasing 12% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.28/kWh fleet rate (Ofgem, 2024)",
            "Diesel cost: £1.42/litre commercial rate (DfT, 2024)",
            "HGV grants available up to £25,000 (OZEV, 2024)",
            "Insurance premium 25% higher for electric (RHA, 2024)",
            "Maintenance costs 50% lower for electric (Logistics UK, 2024)"
        ]
    },
    "hgv_rigid_medium": {
        "name": "Rigid HGV 12-18t",
        "electric_price": 180000,
        "diesel_price": 85000,
        "electric_efficiency": 1.6,
        "diesel_efficiency": 10,
        "default_mileage": 45000,
        "grant": 40000,
        "test_frequency": "Annual MOT from first use, 6-weekly roadworthiness tests",
        "assumptions": [
            "Electric HGV price decreasing 12% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.28/kWh fleet rate (Ofgem, 2024)",
            "Diesel cost: £1.42/litre commercial rate (DfT, 2024)",
            "HGV grants available up to £40,000 (OZEV, 2024)",
            "Insurance premium 25% higher for electric (RHA, 2024)",
            "Maintenance costs 50% lower for electric (Logistics UK, 2024)"
        ]
    },
    "hgv_rigid_large": {
        "name": "Rigid HGV 18-26t",
        "electric_price": 220000,
        "diesel_price": 105000,
        "electric_efficiency": 1.4,
        "diesel_efficiency": 9,
        "default_mileage": 50000,
        "grant": 40000,
        "test_frequency": "Annual MOT from first use, 6-weekly roadworthiness tests",
        "assumptions": [
            "Electric HGV price decreasing 12% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.28/kWh fleet rate (Ofgem, 2024)",
            "Diesel cost: £1.42/litre commercial rate (DfT, 2024)",
            "HGV grants available up to £40,000 (OZEV, 2024)",
            "Insurance premium 25% higher for electric (RHA, 2024)",
            "Maintenance costs 50% lower for electric (Logistics UK, 2024)"
        ]
    },
    "hgv_artic_small": {
        "name": "Articulated HGV 26-32t",
        "electric_price": 280000,
        "diesel_price": 120000,
        "electric_efficiency": 1.2,
        "diesel_efficiency": 8.5,
        "default_mileage": 80000,
        "grant": 40000,
        "test_frequency": "Annual MOT from first use, 6-weekly roadworthiness tests",
        "assumptions": [
            "Electric HGV price decreasing 15% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.25/kWh fleet rate with demand management (Ofgem, 2024)",
            "Diesel cost: £1.40/litre bulk commercial rate (DfT, 2024)",
            "HGV grants available up to £40,000 (OZEV, 2024)",
            "Insurance premium 30% higher for electric (RHA, 2024)",
            "Maintenance costs 55% lower for electric (Logistics UK, 2024)"
        ]
    },
    "hgv_artic_large": {
        "name": "Articulated HGV 32-44t",
        "electric_price": 350000,
        "diesel_price": 140000,
        "electric_efficiency": 1.0,
        "diesel_efficiency": 8,
        "default_mileage": 100000,
        "grant": 40000,
        "test_frequency": "Annual MOT from first use, 6-weekly roadworthiness tests",
        "assumptions": [
            "Electric HGV price decreasing 15% annually (Carbon Trust, 2024)",
            "Electricity cost: £0.25/kWh fleet rate with demand management (Ofgem, 2024)",
            "Diesel cost: £1.40/litre bulk commercial rate (DfT, 2024)",
            "HGV grants available up to £40,000 (OZEV, 2024)",
            "Insurance premium 30% higher for electric (RHA, 2024)",
            "Maintenance costs 55% lower for electric (Logistics UK, 2024)"
        ]
    }
}


def format_currency(amount):
    """Format currency with UK formatting"""
    return f"£{amount:,.0f}"


def calculate_electric_costs(vehicle, purchase_price, annual_mileage, years):
    """Calculate electric vehicle costs"""
    total_mileage = annual_mileage * years
    
    # Energy rate based on vehicle type
    energy_rate = 0.35  # Default for vans
    if 'Large Van' in vehicle['name']:
        energy_rate = 0.32
    elif 'HGV' in vehicle['name']:
        energy_rate = 0.25 if 'Articulated' in vehicle['name'] else 0.28
    
    # Calculate energy cost
    if 'HGV' in vehicle['name']:
        # HGV efficiency in miles/kWh
        energy_cost = (total_mileage / vehicle['electric_efficiency']) * energy_rate
    else:
        # Van efficiency in kWh/mile
        energy_cost = total_mileage * vehicle['electric_efficiency'] * energy_rate
    
    # Calculate other costs
    maintenance_multiplier = 0.6 if 'van' in vehicle['name'].lower() else 0.5  # 40-50% lower
    maintenance_cost = (0.08 if 'van' in vehicle['name'].lower() else 0.12) * total_mileage * maintenance_multiplier
    
    annual_insurance = 3500 if 'HGV' in vehicle['name'] else 1200
    insurance_multiplier = 1.25 if 'HGV' in vehicle['name'] else 1.15  # 15-25% higher
    insurance_cost = annual_insurance * years * insurance_multiplier
    
    net_purchase_price = purchase_price - vehicle['grant']
    
    return {
        'purchase': net_purchase_price,
        'energy': energy_cost,
        'maintenance': maintenance_cost,
        'insurance': insurance_cost,
        'total': net_purchase_price + energy_cost + maintenance_cost + insurance_cost
    }


def calculate_diesel_costs(vehicle, purchase_price, annual_mileage, years):
    """Calculate diesel vehicle costs"""
    total_mileage = annual_mileage * years
    diesel_price = 1.42 if 'HGV' in vehicle['name'] else 1.45  # £/litre
    
    # Fuel cost calculation
    fuel_cost = (total_mileage / vehicle['diesel_efficiency']) * diesel_price * 4.546  # Convert to litres
    
    # Maintenance cost
    maintenance_cost = (0.08 if 'van' in vehicle['name'].lower() else 0.12) * total_mileage
    
    # Insurance cost
    annual_insurance = 3500 if 'HGV' in vehicle['name'] else 1200
    insurance_cost = annual_insurance * years
    
    return {
        'purchase': purchase_price,
        'energy': fuel_cost,
        'maintenance': maintenance_cost,
        'insurance': insurance_cost,
        'total': purchase_price + fuel_cost + maintenance_cost + insurance_cost
    }


def calculate_electricity_demand(vehicle_key, annual_mileage, num_vehicles):
    """Calculate annual electricity demand in kWh"""
    vehicle = VEHICLE_DATA[vehicle_key]
    
    if 'HGV' in vehicle['name']:
        # HGV efficiency in miles/kWh, convert to kWh/mile
        efficiency_kwh_per_mile = 1 / vehicle['electric_efficiency']
    else:
        # Van efficiency already in kWh/mile
        efficiency_kwh_per_mile = vehicle['electric_efficiency']
    
    annual_kwh = annual_mileage * efficiency_kwh_per_mile * num_vehicles
    return round(annual_kwh)


def save_calculation_data(vehicle_type, num_vehicles, postcode, purchase_year, annual_mileage):
    """Save calculation data to CSV for harvesting"""
    try:
        calculation_record = {
            'timestamp': datetime.now().isoformat(),
            'vehicle_type': vehicle_type,
            'num_vehicles': num_vehicles,
            'postcode': postcode.upper(),
            'purchase_year': purchase_year,
            'annual_mileage': annual_mileage,
            'estimated_electricity_demand': calculate_electricity_demand(vehicle_type, annual_mileage, num_vehicles)
        }
        
        file_path = 'data/calculations.csv'
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['timestamp', 'vehicle_type', 'num_vehicles', 'postcode', 
                         'purchase_year', 'annual_mileage', 'estimated_electricity_demand']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(calculation_record)
    except Exception as e:
        st.error(f"Error saving data: {e}")


# Main Streamlit App
def main():
    st.title("🚛 HGV/Van Electric versus Diesel Calculator")
    st.markdown("**Compare total cost of ownership and environmental impact for commercial vehicles**")
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle type selection
        vehicle_options = {
            "Small Van (up to 2.5t GVW)": "van_small",
            "Medium Van (2.5-3.5t GVW)": "van_medium", 
            "Large Van (3.5-7.5t GVW)": "van_large",
            "Rigid HGV 7.5-12t": "hgv_rigid_small",
            "Rigid HGV 12-18t": "hgv_rigid_medium",
            "Rigid HGV 18-26t": "hgv_rigid_large",
            "Articulated HGV 26-32t": "hgv_artic_small",
            "Articulated HGV 32-44t": "hgv_artic_large"
        }
        
        selected_vehicle_name = st.selectbox("Vehicle Type", list(vehicle_options.keys()))
        vehicle_type = vehicle_options[selected_vehicle_name]
        vehicle = VEHICLE_DATA[vehicle_type]
        
        num_vehicles = st.number_input("Number of Vehicles", min_value=1, max_value=100, value=1)
        postcode = st.text_input("Postcode", placeholder="e.g. SW1A 1AA", max_chars=8)
        
    with col2:
        purchase_year = st.selectbox("Planned Purchase Year", 
                                   options=list(range(2025, 2033)), 
                                   index=0)
        
        annual_mileage = st.number_input("Annual Mileage", 
                                       min_value=1000, 
                                       max_value=200000, 
                                       value=vehicle['default_mileage'],
                                       step=1000)
        
        operating_period = st.selectbox("Operating Period (Years)", 
                                      options=[3, 5, 7, 10], 
                                      index=1)
    
    # Calculate button
    if st.button("🔄 Calculate Costs", type="primary"):
        if annual_mileage and vehicle_type:
            # Price adjustments based on purchase year
            years_from_now = purchase_year - 2025
            
            # Electric price reduction rates
            electric_reduction = 0.08  # 8% base
            if 'hgv_rigid' in vehicle_type:
                electric_reduction = 0.12
            elif 'hgv_artic' in vehicle_type:
                electric_reduction = 0.15
            
            adjusted_electric_price = vehicle['electric_price'] * (1 - electric_reduction) ** years_from_now
            adjusted_diesel_price = vehicle['diesel_price'] * (1.02 ** years_from_now)  # 2% increase
            
            # Calculate costs
            electric_costs = calculate_electric_costs(vehicle, adjusted_electric_price, annual_mileage, operating_period)
            diesel_costs = calculate_diesel_costs(vehicle, adjusted_diesel_price, annual_mileage, operating_period)
            
            # Scale for multiple vehicles
            for cost_type in electric_costs:
                electric_costs[cost_type] *= num_vehicles
                diesel_costs[cost_type] *= num_vehicles
            
            # Display results
            st.header("💰 Cost Comparison Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("⚡ Electric Vehicle")
                st.metric("Purchase Cost (after grants)", format_currency(electric_costs['purchase']))
                st.metric("Energy Costs", format_currency(electric_costs['energy']))
                st.metric("Maintenance", format_currency(electric_costs['maintenance']))
                st.metric("Insurance", format_currency(electric_costs['insurance']))
                st.metric("**Total Cost**", format_currency(electric_costs['total']))
            
            with col2:
                st.subheader("⛽ Diesel Vehicle")
                st.metric("Purchase Cost", format_currency(diesel_costs['purchase']))
                st.metric("Fuel Costs", format_currency(diesel_costs['energy']))
                st.metric("Maintenance", format_currency(diesel_costs['maintenance']))
                st.metric("Insurance", format_currency(diesel_costs['insurance']))
                st.metric("**Total Cost**", format_currency(diesel_costs['total']))
            
            # Savings calculation
            savings = diesel_costs['total'] - electric_costs['total']
            savings_percentage = (savings / diesel_costs['total'] * 100)
            
            if savings > 0:
                st.success(f"💚 Electric vehicles will save you {format_currency(savings)} ({savings_percentage:.1f}%) over the operating period")
            else:
                st.warning(f"⚠️ Electric vehicles will cost {format_currency(abs(savings))} ({abs(savings_percentage):.1f}%) more over the operating period")
            
            # Environmental impact
            co2_per_mile = 0.2 if 'van' in vehicle['name'].lower() else 0.5
            total_mileage = annual_mileage * operating_period * num_vehicles
            co2_saved = (total_mileage * co2_per_mile / 1000)  # Convert to tonnes
            
            st.info(f"🌱 **Environmental Impact**: {co2_saved:.1f} tonnes CO₂ saved by choosing electric over diesel")
            
            # Vehicle testing info
            st.info(f"🔧 **Vehicle Testing**: {vehicle['test_frequency']}")
            
            # Save data for harvesting
            if postcode:
                save_calculation_data(vehicle_type, num_vehicles, postcode, purchase_year, annual_mileage)
                st.success("✅ Calculation data saved for analysis")
    
    # Assumptions section
    st.header("📋 Assumptions and Sources")
    if 'vehicle_type' in locals():
        vehicle = VEHICLE_DATA[vehicle_type]
        for assumption in vehicle['assumptions']:
            st.write(f"• {assumption}")
    
    st.write("**Sources**: Road Haulage Association (RHA), Logistics UK, Carbon Trust, Science Based Targets initiative (SBTi), Department for Transport (DfT), Energy and Climate Intelligence Unit (ECIU), Society of Motor Manufacturers and Traders (SMMT)")
    
    # Data harvesting section (admin view)
    with st.sidebar:
        st.header("📊 Admin: Data Analysis")
        if st.button("📈 View Demand Summary"):
            try:
                if os.path.exists('data/calculations.csv'):
                    df = pd.read_csv('data/calculations.csv')
                    
                    if not df.empty:
                        st.write("**Recent Calculations:**")
                        st.dataframe(df.tail(10))
                        
                        # Summary by postcode
                        if 'postcode' in df.columns:
                            postcode_summary = df.groupby('postcode').agg({
                                'num_vehicles': 'sum',
                                'estimated_electricity_demand': 'sum'
                            }).reset_index()
                            
                            st.write("**Demand by Postcode:**")
                            st.dataframe(postcode_summary)
                            
                            # Download button for data
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download All Data",
                                data=csv,
                                file_name='vehicle_calculations.csv',
                                mime='text/csv'
                            )
                    else:
                        st.write("No calculation data available yet.")
                else:
                    st.write("No calculation data available yet.")
            except Exception as e:
                st.error(f"Error loading data: {e}")


if __name__ == "__main__":
    main()
