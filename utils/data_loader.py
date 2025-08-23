"""
Data loading and preprocessing utility functions
"""

import json
import pandas as pd
import streamlit as st
from typing import Dict, List, Any
import os

@st.cache_data(ttl=300, show_spinner="Loading data...")
def load_data() -> Dict[str, Any]:
    """
    Load and cache data.json file.
    
    Returns:
        Dict: Loaded data
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Data file not found.")
        return {}
    except json.JSONDecodeError:
        st.error("Data file format is invalid.")
        return {}

def get_companies() -> List[str]:
    """
    Returns list of available companies.
    
    Returns:
        List[str]: List of company names
    """
    data = load_data()
    return data.get('metadata', {}).get('companies', [])

def get_years() -> List[str]:
    """
    Returns list of available years.
    
    Returns:
        List[str]: List of years
    """
    data = load_data()
    return data.get('metadata', {}).get('years', [])

@st.cache_data(ttl=300)
def get_latest_year_data() -> pd.DataFrame:
    """
    Returns all company data for the latest year as DataFrame.
    
    Returns:
        pd.DataFrame: Latest year data
    """
    data = load_data()
    years = get_years()
    
    if not years:
        return pd.DataFrame()
    
    latest_year = max(years, key=int)
    
    rows = []
    for key, company_data in data.items():
        if key == 'metadata':
            continue
            
        if company_data.get('year') == int(latest_year):
            row = {
                'Company': company_data.get('company_name', ''),
                'Year': company_data.get('year', ''),
                'Accident Rate (‰)': company_data.get('accident_rate', 0),
                'Fatalities': company_data.get('fatality_rate', 0),
                'Safety Audit Compliance (%)': company_data.get('safety_inspection_compliance_rate', 0),
                'Carbon Emissions (tCO₂e)': company_data.get('carbon_emissions', 0),
                'Energy Consumption (kWh/㎡)': company_data.get('energy_consumption', 0),
                'Renewable Energy Ratio (%)': company_data.get('renewable_energy_ratio', 0),
                'Renewable Energy Amount (GWh)': company_data.get('renewable_energy_amount', 0),
                'Construction Waste (ton)': company_data.get('construction_waste', 0),
                'Recycling Rate (%)': company_data.get('recycling_rate', 0)
            }
            rows.append(row)
    
    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def get_company_trend_data(company: str) -> pd.DataFrame:
    """
    Returns year-over-year trend data for a specific company.
    
    Args:
        company (str): Company name
        
    Returns:
        pd.DataFrame: Year-over-year trend data
    """
    data = load_data()
    
    rows = []
    for key, company_data in data.items():
        if key == 'metadata':
            continue
            
        if company_data.get('company_name') == company:
            row = {
                'Company': company_data.get('company_name', ''),
                'Year': company_data.get('year', ''),
                'Accident Rate (‰)': company_data.get('accident_rate', 0),
                'Fatalities': company_data.get('fatality_rate', 0),
                'Safety Audit Compliance (%)': company_data.get('safety_inspection_compliance_rate', 0),
                'Carbon Emissions (tCO₂e)': company_data.get('carbon_emissions', 0),
                'Energy Consumption (kWh/㎡)': company_data.get('energy_consumption', 0),
                'Renewable Energy Ratio (%)': company_data.get('renewable_energy_ratio', 0),
                'Renewable Energy Amount (GWh)': company_data.get('renewable_energy_amount', 0),
                'Construction Waste (ton)': company_data.get('construction_waste', 0),
                'Recycling Rate (%)': company_data.get('recycling_rate', 0)
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values('Year')
    return df

@st.cache_data(ttl=300)
def get_multi_company_data(companies: List[str], year: str = None) -> pd.DataFrame:
    """
    Returns data for multiple companies for comparison.
    
    Args:
        companies (List[str]): List of company names
        year (str, optional): Specific year. Uses latest year if None
        
    Returns:
        pd.DataFrame: Multi-company comparison data
    """
    data = load_data()
    
    if year is None:
        years = get_years()
        year = max(years, key=int) if years else '2025'
    
    rows = []
    for key, company_data in data.items():
        if key == 'metadata':
            continue
            
        company_name = company_data.get('company_name')
        data_year = company_data.get('year')
        
        if company_name in companies and data_year == int(year):
            row = {
                'Company': company_name,
                'Year': data_year,
                'Accident Rate (‰)': company_data.get('accident_rate', 0),
                'Fatalities': company_data.get('fatality_rate', 0),
                'Safety Audit Compliance (%)': company_data.get('safety_inspection_compliance_rate', 0),
                'Carbon Emissions (tCO₂e)': company_data.get('carbon_emissions', 0),
                'Energy Consumption (kWh/㎡)': company_data.get('energy_consumption', 0),
                'Renewable Energy Ratio (%)': company_data.get('renewable_energy_ratio', 0),
                'Renewable Energy Amount (GWh)': company_data.get('renewable_energy_amount', 0),
                'Construction Waste (ton)': company_data.get('construction_waste', 0),
                'Recycling Rate (%)': company_data.get('recycling_rate', 0)
            }
            rows.append(row)
    
    return pd.DataFrame(rows)

def get_units() -> Dict[str, str]:
    """
    Returns unit information for each indicator.
    
    Returns:
        Dict[str, str]: Unit information by indicator
    """
    data = load_data()
    return data.get('metadata', {}).get('units', {})

def get_all_company_data_by_year(year: str) -> pd.DataFrame:
    """
    Returns all company data for a specific year.
    
    Args:
        year (str): Year
        
    Returns:
        pd.DataFrame: All company data for the specified year
    """
    data = load_data()
    
    rows = []
    for key, company_data in data.items():
        if key == 'metadata':
            continue
            
        if company_data.get('year') == int(year):
            row = {
                'Company': company_data.get('company_name', ''),
                'Year': company_data.get('year', ''),
                'Accident Rate (‰)': company_data.get('accident_rate', 0),
                'Fatalities': company_data.get('fatality_rate', 0),
                'Safety Audit Compliance (%)': company_data.get('safety_inspection_compliance_rate', 0),
                'Carbon Emissions (tCO₂e)': company_data.get('carbon_emissions', 0),
                'Energy Consumption (kWh/㎡)': company_data.get('energy_consumption', 0),
                'Renewable Energy Ratio (%)': company_data.get('renewable_energy_ratio', 0),
                'Renewable Energy Amount (GWh)': company_data.get('renewable_energy_amount', 0),
                'Construction Waste (ton)': company_data.get('construction_waste', 0),
                'Recycling Rate (%)': company_data.get('recycling_rate', 0)
            }
            rows.append(row)
    
    return pd.DataFrame(rows)