#!/usr/bin/env python3
"""
HGV/Van Electric vs Diesel Calculator - Flask Web Application
Author: Claude Assistant
Description: A web application for comparing electric vs diesel vehicle costs
with backend data collection for demand analysis.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import csv

# Initialize Flask application
app = Flask(__name__)

# Ensure data directory exists for storing calculation results
os.makedirs('data', exist_ok=True)


@app.route('/')
def index():
    """Serve the main calculator page"""
    return render_template('calculator.html')


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Process calculation request and store data for analysis
    
    Expected JSON payload:
    {
        "vehicleType": "van_small|van_medium|...",
        "numVehicles": int,
        "postcode": "string",
        "purchaseYear": int,
        "annualMileage": int
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or not data.get('vehicleType') or not data.get('annualMileage'):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Create calculation record for storage
        calculation_record = {
            'timestamp': datetime.now().isoformat(),
            'vehicle_type': data.get('vehicleType'),
            'num_vehicles': data.get('numVehicles', 1),
            'postcode': data.get('postcode', '').upper(),
            'purchase_year': data.get('purchaseYear'),
            'annual_mileage': data.get('annualMileage'),
            'estimated_electricity_demand': calculate_electricity_demand(
                data.get('vehicleType'), 
                data.get('annualMileage'), 
                data.get('numVehicles', 1)
            )
        }
        
        # Save to CSV file for backend harvesting
        save_to_csv(calculation_record)
        
        return jsonify({'status': 'success', 'data': calculation_record})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/export-data')
def export_data():
    """
    Endpoint for harvesting all stored calculation data
    Returns: JSON array of all calculation records
    """
    try:
        with open('data/calculations.csv', 'r') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        return jsonify({'status': 'success', 'count': len(data), 'data': data})
    except FileNotFoundError:
        return jsonify({'status': 'success', 'count': 0, 'data': []})


@app.route('/api/demand-summary')
def demand_summary():
    """
    Generate summary of electricity demand by postcode
    Returns: Aggregated data showing vehicle counts and electricity demand by location
    """
    try:
        with open('data/calculations.csv', 'r') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        
        # Aggregate by postcode
        postcode_summary = {}
        
        for record in data:
            postcode = record.get('postcode', 'UNKNOWN')
            
            if postcode not in postcode_summary:
                postcode_summary[postcode] = {
                    'total_vehicles': 0,
                    'total_electricity_demand': 0,
                    'hgv_count': 0,
                    'van_count': 0,
                    'calculations_count': 0
                }
            
            # Parse numeric values safely
            try:
                num_vehicles = int(record.get('num_vehicles', 0))
                electricity_demand = int(record.get('estimated_electricity_demand', 0))
            except (ValueError, TypeError):
                num_vehicles = 0
                electricity_demand = 0
            
            # Update totals
            postcode_summary[postcode]['total_vehicles'] += num_vehicles
            postcode_summary[postcode]['total_electricity_demand'] += electricity_demand
            postcode_summary[postcode]['calculations_count'] += 1
            
            # Categorize by vehicle type
            vehicle_type = record.get('vehicle_type', '').lower()
            if 'hgv' in vehicle_type:
                postcode_summary[postcode]['hgv_count'] += num_vehicles
            else:
                postcode_summary[postcode]['van_count'] += num_vehicles
        
        return jsonify({
            'status': 'success', 
            'summary': postcode_summary,
            'total_postcodes': len(postcode_summary)
        })
        
    except FileNotFoundError:
        return jsonify({'status': 'success', 'summary': {}, 'total_postcodes': 0})


def calculate_electricity_demand(vehicle_type, annual_mileage, num_vehicles):
    """
    Calculate estimated annual electricity demand in kWh
    
    Args:
        vehicle_type (str): Type of vehicle (e.g., 'van_small', 'hgv_rigid_small')
        annual_mileage (int): Miles driven per year
        num_vehicles (int): Number of vehicles
    
    Returns:
        int: Annual electricity demand in kWh
    """
    # Vehicle efficiency data (kWh per mile for consistency)
    vehicle_efficiency = {
        'van_small': 3.5,
        'van_medium': 4.2,
        'van_large': 5.8,
        'hgv_rigid_small': 1/1.8,    # Convert miles/kWh to kWh/mile
        'hgv_rigid_medium': 1/1.6,
        'hgv_rigid_large': 1/1.4,
        'hgv_artic_small': 1/1.2,
        'hgv_artic_large': 1/1.0,
    }
    
    try:
        efficiency = vehicle_efficiency.get(vehicle_type, 3.5)  # Default to small van
        annual_kwh = int(annual_mileage) * efficiency * int(num_vehicles)
        return round(annual_kwh)
    except (ValueError, TypeError):
        return 0


def save_to_csv(record):
    """
    Save calculation record to CSV file for data harvesting
    
    Args:
        record (dict): Calculation data to save
    """
    file_path = 'data/calculations.csv'
    file_exists = os.path.isfile(file_path)
    
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            fieldnames = [
                'timestamp', 'vehicle_type', 'num_vehicles', 'postcode', 
                'purchase_year', 'annual_mileage', 'estimated_electricity_demand'
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(record)
            
    except Exception as e:
        print(f"Error saving to CSV: {e}")


if __name__ == '__main__':
    print("Starting HGV/Van Electric vs Diesel Calculator")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
