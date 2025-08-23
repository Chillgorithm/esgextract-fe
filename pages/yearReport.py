"""
연도별 비교 페이지
특정 회사의 연도별 ESG 지표 트렌드를 시각화
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
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

# 페이지 설정
st.set_page_config(
    page_title="연도별 비교 분석",
    page_icon="📈",
    layout="wide"
)

# 커스텀 CSS
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
    """메인 함수"""
    
    # 헤더
    st.markdown('<div class="main-header">📈 연도별 비교 분석</div>', 
                unsafe_allow_html=True)
    
    # 뒤로가기 버튼
    if st.button("🏠 메인으로 돌아가기", type="secondary"):
        if 'analysis_mode' in st.session_state:
            del st.session_state.analysis_mode
        st.switch_page("main.py")
    
    # 최신 연도 데이터 테이블 표시
    show_latest_data_table()
    
    # 회사 선택 및 트렌드 분석
    show_company_trend_analysis()

def show_latest_data_table():
    """최신 연도 데이터 테이블 표시"""
    st.markdown("---")
    st.markdown('<div class="sub-header">📊 최신 연도 데이터 (2025년)</div>', 
                unsafe_allow_html=True)
    
    try:
        latest_data = get_latest_year_data()
        if not latest_data.empty:
            # 데이터 포맷팅
            formatted_data = latest_data.copy()
            
            # 수치 컬럼 포맷팅
            numeric_columns = [
                '사고율(‰)', '사망자수', '안전감사 준수율(%)', '산재보험금(백만원)',
                '탄소배출량(tCO₂e)', '에너지사용량(kWh/㎡)', '재생에너지비율(%)',
                '건설폐기물(ton)', '재활용률(%)'
            ]
            
            for col in numeric_columns:
                if col in formatted_data.columns:
                    if '(%)' in col:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}%")
                    elif col == '사고율(‰)':
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}‰")
                    elif col in ['탄소배출량(tCO₂e)', '건설폐기물(ton)']:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:,.0f}")
                    else:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(
                formatted_data.drop('연도', axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")

def show_company_trend_analysis():
    """회사별 트렌드 분석"""
    st.markdown("---")
    st.markdown('<div class="sub-header">🏢 회사별 연도별 트렌드 분석</div>', 
                unsafe_allow_html=True)
    
    # 회사 선택
    st.markdown('<div class="company-selector">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        companies = get_companies()
        selected_company = st.selectbox(
            "분석할 회사를 선택하세요:",
            companies,
            index=0 if companies else None,
            key="year_company_selector"
        )
    
    with col2:
        # 연도 범위 선택
        years = get_years()
        year_range = st.select_slider(
            "연도 범위 선택:",
            options=years,
            value=(years[0], years[-1]) if len(years) > 1 else years,
            key="year_range_selector"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 선택된 회사와 연도 범위 표시
    if selected_company:
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"🏢 **선택된 회사:** {selected_company}")
        with col_info2:
            if isinstance(year_range, tuple):
                st.info(f"📅 **분석 기간:** {year_range[0]} ~ {year_range[1]}")
            else:
                st.info(f"📅 **분석 연도:** {year_range}")
    
    if selected_company:
        # 트렌드 데이터 로드
        trend_data = get_company_trend_data(selected_company)
        
        if not trend_data.empty:
            # 연도 범위에 따른 데이터 필터링
            if isinstance(year_range, tuple):
                start_year, end_year = year_range
                filtered_data = trend_data[
                    (trend_data['연도'] >= start_year) & 
                    (trend_data['연도'] <= end_year)
                ]
            else:
                filtered_data = trend_data[trend_data['연도'] == year_range]
            
            if not filtered_data.empty:
                # 탭으로 안전/환경 지표 분리
                safety_tab, env_tab = st.tabs(["🔒 안전 지표", "🌱 환경 지표"])
                
                with safety_tab:
                    show_safety_charts(filtered_data, selected_company)
                
                with env_tab:
                    show_environment_charts(filtered_data, selected_company)
            else:
                st.warning("선택한 연도 범위에 해당하는 데이터가 없습니다.")
        else:
            st.warning(f"{selected_company}의 데이터를 찾을 수 없습니다.")

def show_safety_charts(data: pd.DataFrame, company: str):
    """안전 지표 차트 표시"""
    
    # 데이터 정렬 (연도순)
    data = data.sort_values('연도')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 사고율 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📉 사고율 추이")
        
        accident_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_safety_color('사고율')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('사고율(‰):Q', title='사고율 (‰)', scale=alt.Scale(zero=False)),
            tooltip=['연도:O', '사고율(‰):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 사고율 연도별 추이"
        ).interactive()
        
        st.altair_chart(accident_chart, use_container_width=True)
        
        # 간단한 인사이트 표시
        if len(data) > 1:
            current_rate = data.iloc[-1]['사고율(‰)']
            previous_rate = data.iloc[-2]['사고율(‰)'] if len(data) > 1 else current_rate
            change = current_rate - previous_rate
            
            if abs(change) > 0.1:
                trend_color = "🔻" if change < 0 else "🔺"
                st.info(f"{trend_color} 전년 대비 {abs(change):.1f}‰ {'감소' if change < 0 else '증가'}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 안전감사 준수율 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 안전감사 준수율 추이")
        
        audit_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_safety_color('안전감사')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('안전감사 준수율(%):Q', title='준수율 (%)', scale=alt.Scale(domain=[90, 100])),
            tooltip=['연도:O', '안전감사 준수율(%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 안전감사 준수율 연도별 추이"
        ).interactive()
        
        st.altair_chart(audit_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 사망자수 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ 사망자수 추이")
        
        fatality_chart = alt.Chart(data).mark_bar(
            color=get_safety_color('사망자수'),
            width=50
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('사망자수:Q', title='사망자수 (명)'),
            tooltip=['연도:O', '사망자수:Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 사망자수 연도별 추이"
        ).interactive()
        
        st.altair_chart(fatality_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 산재보험금 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 💰 산재보험금 추이")
        
        compensation_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_safety_color('산재보험금')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('산재보험금(백만원):Q', title='보험금 (백만원)', scale=alt.Scale(zero=False)),
            tooltip=['연도:O', '산재보험금(백만원):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 산재보험금 연도별 추이"
        ).interactive()
        
        st.altair_chart(compensation_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_environment_charts(data: pd.DataFrame, company: str):
    """환경 지표 차트 표시"""
    
    # 데이터 정렬 (연도순)
    data = data.sort_values('연도')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 탄소배출량 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🌍 탄소배출량 추이")
        
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
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('탄소배출량(tCO₂e):Q', title='탄소배출량 (tCO₂e)'),
            tooltip=['연도:O', '탄소배출량(tCO₂e):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 탄소배출량 연도별 추이"
        ).interactive()
        
        st.altair_chart(carbon_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 재생에너지비율 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ 재생에너지비율 추이")
        
        renewable_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('재생에너지')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('재생에너지비율(%):Q', title='재생에너지비율 (%)', scale=alt.Scale(domain=[0, 70])),
            tooltip=['연도:O', '재생에너지비율(%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 재생에너지비율 연도별 추이"
        ).interactive()
        
        st.altair_chart(renewable_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 재활용률 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ♻️ 재활용률 추이")
        
        recycling_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('재활용률')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('재활용률(%):Q', title='재활용률 (%)', scale=alt.Scale(domain=[70, 100])),
            tooltip=['연도:O', '재활용률(%):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 재활용률 연도별 추이"
        ).interactive()
        
        st.altair_chart(recycling_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 에너지사용량 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ 에너지사용량 추이")
        
        energy_chart = alt.Chart(data).mark_line(
            point=True,
            strokeWidth=3,
            color=get_environment_color('에너지사용량')
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('에너지사용량(kWh/㎡):Q', title='에너지사용량 (kWh/㎡)', scale=alt.Scale(zero=False)),
            tooltip=['연도:O', '에너지사용량(kWh/㎡):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 에너지사용량 연도별 추이"
        ).interactive()
        
        st.altair_chart(energy_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 건설폐기물 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🗑️ 건설폐기물 추이")
        
        waste_chart = alt.Chart(data).mark_bar(
            color=get_environment_color('폐기물'),
            width=50
        ).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('연도:O', title='연도'),
            y=alt.Y('건설폐기물(ton):Q', title='건설폐기물 (ton)'),
            tooltip=['연도:O', '건설폐기물(ton):Q']
        ).properties(
            width='container',
            height=300,
            title=f"{company} 건설폐기물 연도별 추이"
        ).interactive()
        
        st.altair_chart(waste_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
