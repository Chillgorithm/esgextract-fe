"""
ESG Construction Company Data Dashboard
Main Page
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import (
    load_data, 
    get_companies, 
    get_years, 
    get_latest_year_data
)

# Page configuration
st.set_page_config(
    page_title="ESG Construction Company Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    .metric-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f8ff 100%);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #d1ecf1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1565c0;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #546e7a;
        font-weight: 500;
    }
    
    .mode-selector {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
    }
    
    /* 반응형 차트 컨테이너 */
    .chart-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        overflow-x: auto;
    }
    
    /* 모바일 대응 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .chart-container {
            padding: 0.5rem;
        }
        
        .mode-selector {
            padding: 1rem;
        }
    }
    
    /* 태블릿 대응 */
    @media (max-width: 1024px) {
        .main-header {
            font-size: 2.2rem;
        }
    }
    
    /* 애니메이션 효과 */
    .chart-container {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.02);
    }
    
    .mode-selector button:hover {
        transform: translateY(-1px);
        transition: transform 0.2s ease;
    }
    
    /* 페이드인 애니메이션 */
    .main-header {
        animation: fadeInDown 0.8s ease-out;
    }
    
    .info-box {
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    .mode-selector {
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 로딩 스피너 */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #1f77b4;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-top: 10px;
    }
    
    /* 프로그레스 바 */
    .progress-container {
        width: 100%;
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
        height: 8px;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        animation: progress 2s ease-in-out;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main page function"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem;">
            ESGExtract
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0; font-weight: 300;">
            Construction Company ESG Data Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)
    

    
    # Mode selection section
    st.markdown('### 📊 Select Analysis Mode')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Year-over-Year Analysis", use_container_width=True, type="secondary"):
            st.session_state.analysis_mode = "year_comparison"
            st.rerun()
    
    with col2:
        if st.button("🏢 Company Comparison Analysis", use_container_width=True, type="secondary"):
            st.session_state.analysis_mode = "company_comparison"
            st.rerun()
    
    # Display selected mode and page routing
    if 'analysis_mode' in st.session_state:
        if st.session_state.analysis_mode == "year_comparison":
            show_year_comparison_page()
        elif st.session_state.analysis_mode == "company_comparison":
            show_company_comparison_page()
    else:
        # Display data overview by default
        show_data_overview()

def show_data_overview():
    """Data overview page"""
    st.markdown("---")
    st.markdown('### 📋 Data Overview')
    
    # Basic information
    companies = get_companies()
    years = get_years()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(companies)} Companies</div>
            <div class="metric-label">Analysis Target</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{min(years)} - {max(years)}</div>
            <div class="metric-label">Data Period</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">9 Indicators</div>
            <div class="metric-label">ESG Metrics</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Separator and spacing
    st.markdown("---")
    
    # Latest year data table
    st.markdown("### 📊 Latest Year Data (2025)")
    
    with st.spinner("📊 Loading data..."):
        try:
            # Display progress bar
            progress_placeholder = st.empty()
            progress_placeholder.markdown("""
            <div class="progress-container">
                <div class="progress-bar" style="width: 100%;"></div>
            </div>
            <div class="loading-text">Loading ESG data...</div>
            """, unsafe_allow_html=True)
            
            latest_data = get_latest_year_data()
            progress_placeholder.empty()  # Remove progress bar
            
            if not latest_data.empty:
                # Data formatting
                formatted_data = latest_data.copy()
            
                # Format numeric columns
                numeric_columns = [
                    'Accident Rate (‰)', 'Fatalities', 'Safety Audit Compliance (%)', 'Renewable Energy Amount (GWh)',
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
                
                # CSV download button
                csv_data = latest_data.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"ESG_Data_{latest_data.iloc[0]['Year']}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Unable to load data.")
        except Exception as e:
            st.error(f"An error occurred while loading data: {e}")
    
    # Usage guide
    with st.expander("🆘 Usage Guide"):
        st.markdown("""
        ### 📚 **Dashboard Usage Guide**
        
        #### 🏠 **Main Page** (Current Page)
        - **View Latest Data**: Check all companies' ESG indicators for 2025 at a glance
        - **CSV Download**: Export data using the download button below the table
        
        #### 📈 **Year-over-Year Mode**
        1. Select **company to analyze** from the sidebar
        2. Choose **year range** (using slider)
        3. Check accident rate, fatalities, safety audit compliance trends in **Safety Metrics** tab
        4. Check carbon emissions, energy usage, renewable energy ratio, recycling rate trends in **Environmental Metrics** tab
        
        #### 🏢 **Company Comparison Mode**
        1. Select **companies to compare** from sidebar (up to 5)
        2. Compare safety performance between companies in **Safety Metrics** tab
        3. Compare environmental performance between companies in **Environmental Metrics** tab
        4. Check comprehensive ESG scores and radar charts in **Ranking Analysis** tab
        
        #### 💡 **Tips**
        - Hover over charts to see **detailed data**
        - Use mouse wheel to **zoom in/out** on charts
        - Charts are **touch-enabled** on mobile devices
        - Use **CSV download** to get data for additional analysis
        
        #### ⌨️ **Keyboard Shortcuts**
        - **F5**: Refresh page
        - **Ctrl/Cmd + D**: Download CSV (on applicable pages)
        - **Esc**: Close expanded sections
        - **Tab**: Move to next element
        - **Shift + Tab**: Move to previous element
        """)
        
    # Keyboard shortcut script
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + D for download
        if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
            event.preventDefault();
            const downloadBtn = document.querySelector('[data-testid="stDownloadButton"] button');
            if (downloadBtn) {
                downloadBtn.click();
            }
        }
        
        // Esc to close expandable sections
        if (event.key === 'Escape') {
            const openExpanders = document.querySelectorAll('[data-testid="stExpander"][aria-expanded="true"]');
            openExpanders.forEach(expander => {
                const button = expander.querySelector('button');
                if (button) button.click();
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 ESG Metrics Description"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔒 Safety Metrics**
            - **Accident Rate (‰)**: Industrial accident rate per thousand workers
            - **Fatalities**: Annual workplace fatalities
            - **Safety Audit Compliance (%)**: Safety regulation compliance rate
            """)
        
        with col2:
            st.markdown("""
            **🌱 Environmental Metrics**
            - **Carbon Emissions (tCO₂e)**: Annual carbon dioxide emissions
            - **Energy Consumption (kWh/㎡)**: Energy consumption per unit area
            - **Renewable Energy Ratio (%)**: Share of renewable energy in total energy
            - **Renewable Energy Amount (GWh)**: Absolute amount of renewable energy
            - **Construction Waste (ton)**: Annual construction waste generation
            - **Recycling Rate (%)**: Waste recycling ratio
            """)

def show_year_comparison_page():
    """Redirect to year-over-year comparison page"""
    st.switch_page("pages/yearReport.py")

def show_company_comparison_page():
    """Redirect to company comparison page"""
    st.switch_page("pages/companyReport.py")

if __name__ == "__main__":
    main()

