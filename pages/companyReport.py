"""
Company Comparison Page
Compare and analyze ESG indicators across multiple companies
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    get_companies, 
    get_years, 
    get_latest_year_data,
    get_multi_company_data
)
from utils.chart_styles import (
    get_safety_color,
    get_environment_color,
    get_company_color,
    ESG_COLORS
)

# Page configuration
st.set_page_config(
    page_title="Company Comparison Analysis",
    page_icon="🏢",
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
    
    .company-selector {
        background-color: #f0f8ff;
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
    
    .selected-companies {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .ranking-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function"""
    
    # Header
    st.markdown('<div class="main-header">🏢 Company Comparison Analysis</div>', 
                unsafe_allow_html=True)
    
    # Back button
    if st.button("🏠 Back to Main", type="secondary"):
        if 'analysis_mode' in st.session_state:
            del st.session_state.analysis_mode
        st.switch_page("main.py")
    
    # Display latest year data table
    show_latest_data_table()
    
    # Company selection and comparison analysis
    show_company_comparison_analysis()

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

def show_company_comparison_analysis():
    """Company comparison analysis"""
    st.markdown("---")
    st.markdown('<div class="sub-header">🔍 Company Comparison Analysis</div>', 
                unsafe_allow_html=True)
    
    # Company selection
    st.markdown('<div class="company-selector">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        companies = get_companies()
        selected_companies = st.multiselect(
            "Select companies to compare (max 5):",
            companies,
            default=companies[:3] if len(companies) >= 3 else companies,
            max_selections=5,
            key="company_multiselect"
        )
    
    with col2:
        # Year selection
        years = get_years()
        selected_year = st.selectbox(
            "Comparison Year:",
            years,
            index=len(years)-1 if years else 0,
            key="company_year_selector"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected companies
    if selected_companies:
        st.markdown('<div class="selected-companies">', unsafe_allow_html=True)
        st.markdown(f"**🏢 Selected Companies:** {', '.join(selected_companies)}")
        st.markdown(f"**📅 Comparison Year:** {selected_year}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Load comparison data
        comparison_data = get_multi_company_data(selected_companies, selected_year)
        
        if not comparison_data.empty:
            # Separate safety/environmental indicators into tabs
            safety_tab, env_tab, ranking_tab = st.tabs(["🔒 Safety Metrics", "🌱 Environmental Metrics", "🏆 Overall Ranking"])
            
            with safety_tab:
                show_safety_comparison_charts(comparison_data)
            
            with env_tab:
                show_environment_comparison_charts(comparison_data)
            
            with ranking_tab:
                show_ranking_analysis(comparison_data)
        else:
            st.error("❌ Unable to find data for the selected companies.")
            st.info("💡 **Solution**: Please select different companies or companies with data for the latest year.")
    else:
        st.info("ℹ️ Please select companies to compare.")
        
        # Improved guidance message
        st.markdown("""
        ### 📋 **How to Use**
        1. Select companies to compare from the **dropdown above**
        2. You can select **up to 5 companies**
        3. View **ESG indicator comparisons** for the selected companies
        """)
        
        # Display available companies list
        available_companies = get_companies()
        if available_companies:
            st.write("📋 **Available Companies:**")
            cols = st.columns(3)
            for i, company in enumerate(available_companies):
                with cols[i % 3]:
                    st.write(f"• {company}")

def show_safety_comparison_charts(data: pd.DataFrame):
    """Display safety indicator comparison charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Accident rate comparison bar chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📉 Accident Rate Comparison by Company")
        
        accident_chart = alt.Chart(data).mark_bar(color=get_safety_color('사고율')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Accident Rate (‰)', order='ascending')),
            y=alt.Y('Accident Rate (‰):Q', title='Accident Rate (‰)'),
            tooltip=['Company:N', 'Accident Rate (‰):Q']
        ).properties(
            width='container',
            height=300,
            title="Accident Rate Comparison by Company (Lower is Better)"
        ).interactive()
        
        st.altair_chart(accident_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Safety audit compliance comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 Safety Audit Compliance Comparison by Company")
        
        audit_chart = alt.Chart(data).mark_bar(color=get_safety_color('안전감사')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Safety Audit Compliance (%)', order='descending')),
            y=alt.Y('Safety Audit Compliance (%):Q', title='Compliance Rate (%)', scale=alt.Scale(domain=[90, 100])),
            tooltip=['Company:N', 'Safety Audit Compliance (%):Q']
        ).properties(
            width='container',
            height=300,
            title="Safety Audit Compliance Comparison by Company (Higher is Better)"
        ).interactive()
        
        st.altair_chart(audit_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Fatality comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ Fatality Comparison by Company")
        
        fatality_chart = alt.Chart(data).mark_bar(color=get_safety_color('사망자수')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Fatalities', order='ascending')),
            y=alt.Y('Fatalities:Q', title='Fatalities (count)'),
            tooltip=['Company:N', 'Fatalities:Q']
        ).properties(
            width='container',
            height=300,
            title="Fatality Comparison by Company (Lower is Better)"
        ).interactive()
        
        st.altair_chart(fatality_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Safety indicators completion notice
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.info("✅ Safety indicator analysis completed. Check environmental indicators in the **Environmental Metrics** tab.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_environment_comparison_charts(data: pd.DataFrame):
    """Display environmental indicator comparison charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Carbon Emissions Comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🌍 Carbon Emissions Comparison by Company")
        
        carbon_chart = alt.Chart(data).mark_bar(color=get_environment_color('탄소배출량')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Carbon Emissions (tCO₂e)', order='ascending')),
            y=alt.Y('Carbon Emissions (tCO₂e):Q', title='Carbon Emissions (tCO₂e)'),
            tooltip=['Company:N', 'Carbon Emissions (tCO₂e):Q']
        ).properties(
            width='container',
            height=300,
            title="Carbon Emissions Comparison by Company (Lower is Better)"
        ).interactive()
        
        st.altair_chart(carbon_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Renewable Energy Ratio Comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Renewable Energy Ratio Comparison by Company")
        
        renewable_chart = alt.Chart(data).mark_bar(color=get_environment_color('재생에너지')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Renewable Energy Ratio (%)', order='descending')),
            y=alt.Y('Renewable Energy Ratio (%):Q', title='Renewable Energy Ratio (%)'),
            tooltip=['Company:N', 'Renewable Energy Ratio (%):Q']
        ).properties(
            width='container',
            height=300,
            title="Renewable Energy Ratio Comparison by Company (Higher is Better)"
        ).interactive()
        
        st.altair_chart(renewable_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Renewable Energy Amount Comparison (newly added)
        if 'Renewable Energy Amount (GWh)' in data.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### ⚡ Renewable Energy Amount Comparison by Company")
            
            # Handle null values
            energy_data = data.dropna(subset=['Renewable Energy Amount (GWh)'])
            
            if not energy_data.empty:
                energy_amount_chart = alt.Chart(energy_data).mark_bar(color=get_environment_color('재생에너지')).add_selection(
                    alt.selection_point()
                ).encode(
                    x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Renewable Energy Amount (GWh)', order='descending')),
                    y=alt.Y('Renewable Energy Amount (GWh):Q', title='Renewable Energy Amount (GWh)'),
                    tooltip=['Company:N', 'Renewable Energy Amount (GWh):Q']
                ).properties(
                    width='container',
                    height=300,
                    title="Renewable Energy Amount Comparison by Company (Higher is Better)"
                ).interactive()
                
                st.altair_chart(energy_amount_chart, use_container_width=True)
            else:
                st.info("Renewable energy amount data is not yet available.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recycling Rate Comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ♻️ Recycling Rate Comparison by Company")
        
        recycling_chart = alt.Chart(data).mark_bar(color=get_environment_color('재활용률')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Recycling Rate (%)', order='descending')),
            y=alt.Y('Recycling Rate (%):Q', title='Recycling Rate (%)'),
            tooltip=['Company:N', 'Recycling Rate (%):Q']
        ).properties(
            width='container',
            height=300,
            title="Recycling Rate Comparison by Company (Higher is Better)"
        ).interactive()
        
        st.altair_chart(recycling_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Energy Consumption Comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Energy Consumption Comparison by Company")
        
        energy_chart = alt.Chart(data).mark_bar(color=get_environment_color('에너지사용량')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Energy Consumption (kWh/㎡)', order='ascending')),
            y=alt.Y('Energy Consumption (kWh/㎡):Q', title='Energy Consumption (kWh/㎡)'),
            tooltip=['Company:N', 'Energy Consumption (kWh/㎡):Q']
        ).properties(
            width='container',
            height=300,
            title="Energy Consumption Comparison by Company (Lower is Better)"
        ).interactive()
        
        st.altair_chart(energy_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Construction Waste Comparison
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🗑️ Construction Waste Comparison by Company")
        
        waste_chart = alt.Chart(data).mark_bar(color=get_environment_color('폐기물')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Construction Waste (ton)', order='ascending')),
            y=alt.Y('Construction Waste (ton):Q', title='Construction Waste (ton)'),
            tooltip=['Company:N', 'Construction Waste (ton):Q']
        ).properties(
            width='container',
            height=300,
            title="Construction Waste Comparison by Company (Lower is Better)"
        ).interactive()
        
        st.altair_chart(waste_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_ranking_analysis(data: pd.DataFrame):
    """Overall ranking analysis"""
    
    # Calculate ESG scores
    scoring_data = calculate_esg_scores(data)
    
    # Overall ranking section
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown("#### 🏆 Comprehensive ESG Ranking")
    
    # Display rankings in columns
    rank_cols = st.columns(min(len(scoring_data), 5))  # Maximum 5 columns
    
    for idx, row in scoring_data.iterrows():
        rank = idx + 1
        company = row['Company']
        total_score = row['Overall Score']
        safety_score = row['Safety Score']
        env_score = row['Environmental Score']
        
        with rank_cols[idx % len(rank_cols)]:
            if rank == 1:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #ffd700, #ffed4e); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥇 1st Place</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f} points</strong></p>
                    <small>Safety: {safety_score:.1f} | Environment: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            elif rank == 2:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #c0c0c0, #e8e8e8); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥈 2nd Place</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f} points</strong></p>
                    <small>Safety: {safety_score:.1f} | Environment: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            elif rank == 3:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #cd7f32, #deb887); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥉 3rd Place</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f} points</strong></p>
                    <small>Safety: {safety_score:.1f} | Environment: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #f8f9fa, #e9ecef); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>{rank}th Place</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f} points</strong></p>
                    <small>Safety: {safety_score:.1f} | Environment: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add spacing
    st.markdown("---")
    
    # Separate chart section into two rows
    col1, col2 = st.columns(2)
    
    with col1:
        # ESG Performance Comparison Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🎯 ESG Performance Comparison by Company")
        
        radar_data = prepare_radar_data(scoring_data)
        
        if not radar_data.empty:
            radar_chart = create_radar_chart(radar_data)
            st.altair_chart(radar_chart, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Performance vs Industry Average
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📊 Performance vs Industry Average")
        
        avg_score = scoring_data['Overall Score'].mean()
        
        performance_chart = alt.Chart(scoring_data).mark_bar().encode(
            x=alt.X('Company:N', title='Company', sort=alt.EncodingSortField(field='Overall Score', order='descending')),
            y=alt.Y('Overall Score:Q', title='ESG Score'),
            color=alt.condition(
                alt.datum['Overall Score'] > avg_score,
                alt.value(ESG_COLORS['status']['good']),   # Above average: green
                alt.value(ESG_COLORS['status']['danger'])  # Below average: red
            ),
            tooltip=['Company:N', 'Overall Score:Q', 'Safety Score:Q', 'Environmental Score:Q']
        ).properties(
            width='container',
            height=350,
            title=f"ESG Overall Score (Industry Average: {avg_score:.1f})"
        ).interactive()
        
        # Add average line
        avg_line = alt.Chart(pd.DataFrame({'avg': [avg_score]})).mark_rule(
            color=ESG_COLORS['status']['warning'],
            strokeWidth=2,
            strokeDash=[5, 5]
        ).encode(y='avg:Q')
        
        combined_chart = performance_chart + avg_line
        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional spacing
    st.markdown("---")
    
    # Detailed score table
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 📋 Detailed ESG Score Table")
    
    # Create display dataframe
    display_df = scoring_data[['Company', 'Overall Score', 'Safety Score', 'Environmental Score']].copy()
    display_df.columns = ['Company', 'ESG Overall Score', 'Safety Score', 'Environmental Score']
    
    # Format scores to 1 decimal place
    for col in ['ESG Overall Score', 'Safety Score', 'Environmental Score']:
        display_df[col] = display_df[col].round(1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def calculate_esg_scores(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate ESG scores"""
    
    scoring_data = data.copy()
    
    # Safety score calculation (reverse scoring for lower-is-better indicators)
    scoring_data['Accident Rate Score'] = 100 - (scoring_data['Accident Rate (‰)'] / scoring_data['Accident Rate (‰)'].max()) * 50
    scoring_data['Fatality Score'] = 100 - (scoring_data['Fatalities'] / max(scoring_data['Fatalities'].max(), 1)) * 50
    scoring_data['Safety Audit Score'] = scoring_data['Safety Audit Compliance (%)']
    # Workers' compensation removed from new API
    
    # Environmental score calculation
    scoring_data['Carbon Emissions Score'] = 100 - (scoring_data['Carbon Emissions (tCO₂e)'] / scoring_data['Carbon Emissions (tCO₂e)'].max()) * 50
    scoring_data['Energy Score'] = 100 - (scoring_data['Energy Consumption (kWh/㎡)'] / scoring_data['Energy Consumption (kWh/㎡)'].max()) * 50
    scoring_data['Renewable Energy Score'] = scoring_data['Renewable Energy Ratio (%)'] * 1.5  # Weighted
    scoring_data['Waste Score'] = 100 - (scoring_data['Construction Waste (ton)'] / scoring_data['Construction Waste (ton)'].max()) * 50
    scoring_data['Recycling Score'] = scoring_data['Recycling Rate (%)']
    
    # Category average scores (workers' compensation removed)
    scoring_data['Safety Score'] = (
        scoring_data['Accident Rate Score'] + scoring_data['Fatality Score'] + 
        scoring_data['Safety Audit Score']
    ) / 3
    
    scoring_data['Environmental Score'] = (
        scoring_data['Carbon Emissions Score'] + scoring_data['Energy Score'] + 
        scoring_data['Renewable Energy Score'] + scoring_data['Waste Score'] + scoring_data['Recycling Score']
    ) / 5
    
    # Overall score (Safety 40%, Environmental 60%)
    scoring_data['Overall Score'] = scoring_data['Safety Score'] * 0.4 + scoring_data['Environmental Score'] * 0.6
    
    # Sort by overall score
    scoring_data = scoring_data.sort_values('Overall Score', ascending=False).reset_index(drop=True)
    
    return scoring_data

def prepare_radar_data(scoring_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for radar chart"""
    
    radar_data = []
    
    categories = ['Safety Score', 'Environmental Score']
    
    for _, row in scoring_data.iterrows():
        company = row['Company']
        for category in categories:
            radar_data.append({
                'Company': company,
                'Category': category.replace(' Score', ''),
                'Score': row[category]
            })
    
    return pd.DataFrame(radar_data)

def create_radar_chart(radar_data: pd.DataFrame):
    """Create ESG performance comparison chart"""
    
    # Group bar chart comparing safety/environmental scores by company
    chart = alt.Chart(radar_data).mark_bar().encode(
        x=alt.X('Company:N', title='Company'),
        y=alt.Y('Score:Q', title='Score (0-100)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Category:N', 
                       scale=alt.Scale(domain=['Safety', 'Environmental'], 
                                     range=[ESG_COLORS['status']['danger'], ESG_COLORS['status']['good']]),
                       legend=alt.Legend(title="ESG Domain")),
        xOffset=alt.XOffset('Category:N'),
        tooltip=['Company:N', 'Category:N', 'Score:Q']
    ).properties(
        width='container',
        height=350,
        title="Safety vs Environmental Score Comparison by Company"
    ).interactive()
    
    return chart

if __name__ == "__main__":
    main()
