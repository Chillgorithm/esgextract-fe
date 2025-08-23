"""
Year-over-Year Comparison Page
Visualize ESG indicator trends for specific companies over time
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    get_companies, 
    get_years, 
    get_latest_year_data,
    get_company_trend_data
)
from utils.chart_styles import (
    get_safety_color,
    get_environment_color
)

# Page configuration
st.set_page_config(
    page_title="Year-over-Year Analysis",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    .company-selector {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chart-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function"""
    # Header
    st.markdown('<div class="main-header">📈 Year-over-Year Analysis</div>', 
                unsafe_allow_html=True)
    
    # Back button
    if st.button("🏠 Back to Main", type="secondary"):
        if 'analysis_mode' in st.session_state:
            del st.session_state.analysis_mode
        st.switch_page("main.py")
    
    # Display latest year data table
    show_latest_data_table()
    
    # Company selection and trend analysis
    show_company_trend_analysis()

def show_latest_data_table():
    """Display latest year data table"""
    st.markdown("---")
    st.markdown('<div class="sub-header">📊 Latest Year Data (2025)</div>', 
                unsafe_allow_html=True)
    
    try:
        latest_data = get_latest_year_data()
        if not latest_data.empty:
            # Data formatting
            formatted_data = latest_data.copy()
            
            # Format numeric columns
            numeric_columns = [
                'Accident Rate (‰)', 'Fatalities', 'Safety Audit Compliance (%)',
                'Carbon Emissions (tCO₂e)', 'Energy Consumption (kWh/㎡)', 'Renewable Energy Ratio (%)',
                'Construction Waste (ton)', 'Recycling Rate (%)'
            ]
            
            for col in numeric_columns:
                if col in formatted_data.columns:
                    if '(%)' in col:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}%" if x is not None else "N/A")
                    elif col == 'Accident Rate (‰)':
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}‰" if x is not None else "N/A")
                    elif col in ['Carbon Emissions (tCO₂e)', 'Construction Waste (ton)']:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:,.0f}" if x is not None else "N/A")
                    else:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}" if x is not None else "N/A")
            
            st.dataframe(
                formatted_data.drop('Year', axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Unable to load data.")
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")

def show_company_trend_analysis():
    """Company trend analysis"""
    st.markdown("---")
    st.markdown('<div class="sub-header">🏢 Company Year-over-Year Trend Analysis</div>', 
                unsafe_allow_html=True)
    
    # Company selection
    st.markdown('<div class="company-selector">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        companies = get_companies()
        selected_company = st.selectbox(
            "Select company to analyze:",
            companies,
            index=0 if companies else None,
            key="year_company_selector"
        )
    
    with col2:
        # Year range selection
        years = get_years()
        year_range = st.select_slider(
            "Select Year Range:",
            options=years,
            value=(years[0], years[-1]) if len(years) > 1 else years,
            key="year_range_selector"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected company and year range
    if selected_company:
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"🏢 **Selected Company:** {selected_company}")
        with col_info2:
            if isinstance(year_range, tuple):
                st.info(f"📅 **Analysis Period:** {year_range[0]} ~ {year_range[1]}")
            else:
                st.info(f"📅 **Analysis Year:** {year_range}")
    
    if selected_company:
        # Load trend data
        trend_data = get_company_trend_data(selected_company)
        
        if not trend_data.empty:
            # Filter data by year range (type conversion)
            if isinstance(year_range, tuple):
                start_year, end_year = int(year_range[0]), int(year_range[1])
                filtered_data = trend_data[
                    (trend_data['Year'] >= start_year) & 
                    (trend_data['Year'] <= end_year)
                ]
            else:
                year_value = int(year_range)
                filtered_data = trend_data[trend_data['Year'] == year_value]
            
            if not filtered_data.empty:
                # Separate safety/environmental indicators into tabs
                safety_tab, env_tab = st.tabs(["🔒 Safety Metrics", "🌱 Environmental Metrics"])
                
                with safety_tab:
                    show_safety_charts(filtered_data, selected_company)
                
                with env_tab:
                    show_environment_charts(filtered_data, selected_company)
            else:
                st.warning("No data available for the selected year range.")
        else:
            st.error(f"❌ Unable to find data for {selected_company}.")
            st.info("💡 **Solution**: Please select a different company or adjust the data year range.")
            
            # Display available companies list
            available_companies = get_companies()
            if available_companies:
                st.write("📋 **Available Companies:**")
                for i, company in enumerate(available_companies, 1):
                    st.write(f"  {i}. {company}")

def show_safety_charts(data: pd.DataFrame, company: str):
    """Display safety indicator charts"""
    
    # 데이터 정렬 (연도순)
    data = data.sort_values('Year')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Accident Rate Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📉 Accident Rate Trend")
        
        accident_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_safety_color('사고율')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Accident Rate (‰):Q', title='Accident Rate (‰)', scale=alt.Scale(zero=False)),
            tooltip=['Year:O', 'Accident Rate (‰):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Accident Rate Yearly Trend"
        ).interactive()
        
        st.altair_chart(accident_chart, use_container_width=True)
        
        # 간단한 인사이트 표시
        if len(data) > 1:
            current_rate = data.iloc[-1]['Accident Rate (‰)']
            previous_rate = data.iloc[-2]['Accident Rate (‰)'] if len(data) > 1 else current_rate
            change = current_rate - previous_rate
            
            if abs(change) > 0.1:
                trend_color = "🔻" if change < 0 else "🔺"
                st.info(f"{trend_color} {abs(change):.1f}‰ {'decrease' if change < 0 else 'increase'} compared to previous year")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Safety Audit Compliance Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 Safety Audit Compliance Trend")
        
        audit_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_safety_color('안전감사')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Safety Audit Compliance (%):Q', title='Compliance Rate (%)', scale=alt.Scale(domain=[90, 100])),
            tooltip=['Year:O', 'Safety Audit Compliance (%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Safety Audit Compliance Yearly Trend"
        ).interactive()
        
        st.altair_chart(audit_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Fatalities Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ Fatalities Trend")
        
        fatality_chart = alt.Chart(data).mark_bar(
            color=get_safety_color('사망자수'),
            width=50
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Fatalities:Q', title='Fatalities (count)'),
            tooltip=['Year:O', 'Fatalities:Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Fatalities Yearly Trend"
        ).interactive()
        
        st.altair_chart(fatality_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 안전 지표 완료 안내
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.info("✅ Safety indicator analysis completed. Check environmental indicators in the **Environmental Metrics** tab.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_environment_charts(data: pd.DataFrame, company: str):
    """Display environmental indicator charts"""
    
    # 데이터 정렬 (연도순)
    data = data.sort_values('Year')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Carbon Emissions Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🌍 Carbon Emissions Trend")
        
        carbon_chart = alt.Chart(data).mark_area(
            line={'color': get_environment_color('탄소배출량')},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color=get_environment_color('탄소배출량'), offset=0),
                       alt.GradientStop(color='#FFE5E5', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Carbon Emissions (tCO₂e):Q', title='Carbon Emissions (tCO₂e)'),
            tooltip=['Year:O', 'Carbon Emissions (tCO₂e):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Carbon Emissions Yearly Trend"
        ).interactive()
        
        st.altair_chart(carbon_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Renewable Energy Ratio Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Renewable Energy Ratio Trend")
        
        renewable_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('재생에너지')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Renewable Energy Ratio (%):Q', title='Renewable Energy Ratio (%)', scale=alt.Scale(domain=[0, 70])),
            tooltip=['Year:O', 'Renewable Energy Ratio (%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Renewable Energy Ratio Yearly Trend"
        ).interactive()
        
        st.altair_chart(renewable_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 재생에너지량 차트 (새로 추가)
        if 'Renewable Energy Amount (GWh)' in data.columns:
            energy_data = data.dropna(subset=['Renewable Energy Amount (GWh)'])
            
            if not energy_data.empty:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown("#### ⚡ Renewable Energy Amount Trend")
                
                energy_amount_chart = alt.Chart(energy_data).mark_line(
                    point=True,
                    strokeWidth=3,
                    color=get_environment_color('재생에너지')
                ).add_selection(
                    alt.selection_point()
                ).encode(
                    x=alt.X('Year:O', title='Year'),
                    y=alt.Y('Renewable Energy Amount (GWh):Q', title='Renewable Energy Amount (GWh)', scale=alt.Scale(zero=False)),
                    tooltip=['Year:O', 'Renewable Energy Amount (GWh):Q']
                ).properties(
                    width='container',
                    height=300,
                    title=f"{company} Renewable Energy Amount Yearly Trend"
                ).interactive()
                
                st.altair_chart(energy_amount_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.info("Renewable energy amount data is not yet available.")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Recycling Rate Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ♻️ Recycling Rate Trend")
        
        recycling_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('재활용률')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Recycling Rate (%):Q', title='Recycling Rate (%)', scale=alt.Scale(domain=[70, 100])),
            tooltip=['Year:O', 'Recycling Rate (%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Recycling Rate Yearly Trend"
        ).interactive()
        
        st.altair_chart(recycling_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Energy Consumption Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Energy Consumption Trend")
        
        energy_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('에너지사용량')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Energy Consumption (kWh/㎡):Q', title='Energy Consumption (kWh/㎡)', scale=alt.Scale(zero=False)),
            tooltip=['Year:O', 'Energy Consumption (kWh/㎡):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Energy Consumption Yearly Trend"
        ).interactive()
        
        st.altair_chart(energy_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Construction Waste Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🗑️ Construction Waste Trend")
        
        waste_chart = alt.Chart(data).mark_bar(
            color=get_environment_color('폐기물'),
            width=50
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Construction Waste (ton):Q', title='Construction Waste (ton)'),
            tooltip=['Year:O', 'Construction Waste (ton):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} Construction Waste Yearly Trend"
        ).interactive()
        
        st.altair_chart(waste_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
