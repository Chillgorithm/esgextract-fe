"""
업체별 비교 페이지
여러 업체의 ESG 지표를 비교 분석
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
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

# 페이지 설정
st.set_page_config(
    page_title="업체별 비교 분석",
    page_icon="🏢",
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
    """메인 함수"""
    
    # 헤더
    st.markdown('<div class="main-header">🏢 업체별 비교 분석</div>', 
                unsafe_allow_html=True)
    
    # 뒤로가기 버튼
    if st.button("🏠 메인으로 돌아가기", type="secondary"):
        if 'analysis_mode' in st.session_state:
            del st.session_state.analysis_mode
        st.switch_page("main.py")
    
    # 최신 연도 데이터 테이블 표시
    show_latest_data_table()
    
    # 업체 선택 및 비교 분석
    show_company_comparison_analysis()

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
                '사고율(‰)', '사망자수', '안전감사 준수율(%)',
                '탄소배출량(tCO₂e)', '에너지사용량(kWh/㎡)', '재생에너지비율(%)',
                '건설폐기물(ton)', '재활용률(%)'
            ]
            
            for col in numeric_columns:
                if col in formatted_data.columns:
                    if '(%)' in col:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}%" if x is not None else "N/A")
                    elif col == '사고율(‰)':
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}‰" if x is not None else "N/A")
                    elif col in ['탄소배출량(tCO₂e)', '건설폐기물(ton)']:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:,.0f}" if x is not None else "N/A")
                    else:
                        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.1f}" if x is not None else "N/A")
            
            st.dataframe(
                formatted_data.drop('연도', axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")

def show_company_comparison_analysis():
    """업체별 비교 분석"""
    st.markdown("---")
    st.markdown('<div class="sub-header">🔍 업체별 비교 분석</div>', 
                unsafe_allow_html=True)
    
    # 업체 선택
    st.markdown('<div class="company-selector">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        companies = get_companies()
        selected_companies = st.multiselect(
            "비교할 업체들을 선택하세요 (최대 5개):",
            companies,
            default=companies[:3] if len(companies) >= 3 else companies,
            max_selections=5,
            key="company_multiselect"
        )
    
    with col2:
        # 연도 선택
        years = get_years()
        selected_year = st.selectbox(
            "비교 연도:",
            years,
            index=len(years)-1 if years else 0,
            key="company_year_selector"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 선택된 업체들 표시
    if selected_companies:
        st.markdown('<div class="selected-companies">', unsafe_allow_html=True)
        st.markdown(f"**🏢 선택된 업체:** {', '.join(selected_companies)}")
        st.markdown(f"**📅 비교 연도:** {selected_year}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 비교 데이터 로드
        comparison_data = get_multi_company_data(selected_companies, selected_year)
        
        if not comparison_data.empty:
            # 탭으로 안전/환경 지표 분리
            safety_tab, env_tab, ranking_tab = st.tabs(["🔒 안전 지표", "🌱 환경 지표", "🏆 종합 순위"])
            
            with safety_tab:
                show_safety_comparison_charts(comparison_data)
            
            with env_tab:
                show_environment_comparison_charts(comparison_data)
            
            with ranking_tab:
                show_ranking_analysis(comparison_data)
        else:
            st.error("❌ 선택한 업체들의 데이터를 찾을 수 없습니다.")
            st.info("💡 **해결 방법**: 다른 회사를 선택하거나 최신 연도 데이터가 있는 회사를 선택해주세요.")
    else:
        st.info("ℹ️ 비교할 업체를 선택해주세요.")
        
        # 안내 메시지 개선
        st.markdown("""
        ### 📋 **사용 방법**
        1. **왼쪽 사이드바**에서 비교할 회사를 선택하세요
        2. **최대 5개**까지 선택 가능합니다
        3. 선택된 회사들의 **ESG 지표 비교**를 확인할 수 있습니다
        """)
        
        # 사용 가능한 회사 목록 표시
        available_companies = get_companies()
        if available_companies:
            st.write("📋 **사용 가능한 회사 목록:**")
            cols = st.columns(3)
            for i, company in enumerate(available_companies):
                with cols[i % 3]:
                    st.write(f"• {company}")

def show_safety_comparison_charts(data: pd.DataFrame):
    """안전 지표 비교 차트 표시"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 사고율 비교 바차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📉 업체별 사고율 비교")
        
        accident_chart = alt.Chart(data).mark_bar(color=get_safety_color('사고율')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='사고율(‰)', order='ascending')),
            y=alt.Y('사고율(‰):Q', title='사고율 (‰)'),
            tooltip=['회사:N', '사고율(‰):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 사고율 비교 (낮을수록 좋음)"
        ).interactive()
        
        st.altair_chart(accident_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 안전감사 준수율 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 업체별 안전감사 준수율 비교")
        
        audit_chart = alt.Chart(data).mark_bar(color=get_safety_color('안전감사')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='안전감사 준수율(%)', order='descending')),
            y=alt.Y('안전감사 준수율(%):Q', title='준수율 (%)', scale=alt.Scale(domain=[90, 100])),
            tooltip=['회사:N', '안전감사 준수율(%):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 안전감사 준수율 비교 (높을수록 좋음)"
        ).interactive()
        
        st.altair_chart(audit_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 사망자수 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ 업체별 사망자수 비교")
        
        fatality_chart = alt.Chart(data).mark_bar(color=get_safety_color('사망자수')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='사망자수', order='ascending')),
            y=alt.Y('사망자수:Q', title='사망자수 (명)'),
            tooltip=['회사:N', '사망자수:Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 사망자수 비교 (낮을수록 좋음)"
        ).interactive()
        
        st.altair_chart(fatality_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 안전 지표 완료 안내
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.info("✅ 안전 지표 분석이 완료되었습니다. 환경 지표는 아래 **환경 지표** 탭에서 확인하세요.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_environment_comparison_charts(data: pd.DataFrame):
    """환경 지표 비교 차트 표시"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 탄소배출량 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🌍 업체별 탄소배출량 비교")
        
        carbon_chart = alt.Chart(data).mark_bar(color=get_environment_color('탄소배출량')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='탄소배출량(tCO₂e)', order='ascending')),
            y=alt.Y('탄소배출량(tCO₂e):Q', title='탄소배출량 (tCO₂e)'),
            tooltip=['회사:N', '탄소배출량(tCO₂e):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 탄소배출량 비교 (낮을수록 좋음)"
        ).interactive()
        
        st.altair_chart(carbon_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 재생에너지비율 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ 업체별 재생에너지비율 비교")
        
        renewable_chart = alt.Chart(data).mark_bar(color=get_environment_color('재생에너지')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='재생에너지비율(%)', order='descending')),
            y=alt.Y('재생에너지비율(%):Q', title='재생에너지비율 (%)'),
            tooltip=['회사:N', '재생에너지비율(%):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 재생에너지비율 비교 (높을수록 좋음)"
        ).interactive()
        
        st.altair_chart(renewable_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 재생에너지량 비교 (새로 추가)
        if '재생에너지량(GWh)' in data.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### ⚡ 업체별 재생에너지량 비교")
            
            # null 값이 있는 경우 처리
            energy_data = data.dropna(subset=['재생에너지량(GWh)'])
            
            if not energy_data.empty:
                energy_amount_chart = alt.Chart(energy_data).mark_bar(color=get_environment_color('재생에너지')).add_selection(
                    alt.selection_point()
                ).encode(
                    x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='재생에너지량(GWh)', order='descending')),
                    y=alt.Y('재생에너지량(GWh):Q', title='재생에너지량 (GWh)'),
                    tooltip=['회사:N', '재생에너지량(GWh):Q']
                ).properties(
                    width='container',
                    height=300,
                    title="업체별 재생에너지량 비교 (높을수록 좋음)"
                ).interactive()
                
                st.altair_chart(energy_amount_chart, use_container_width=True)
            else:
                st.info("재생에너지량 데이터가 아직 제공되지 않았습니다.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 재활용률 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ♻️ 업체별 재활용률 비교")
        
        recycling_chart = alt.Chart(data).mark_bar(color=get_environment_color('재활용률')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='재활용률(%)', order='descending')),
            y=alt.Y('재활용률(%):Q', title='재활용률 (%)'),
            tooltip=['회사:N', '재활용률(%):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 재활용률 비교 (높을수록 좋음)"
        ).interactive()
        
        st.altair_chart(recycling_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 에너지사용량 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### ⚡ 업체별 에너지사용량 비교")
        
        energy_chart = alt.Chart(data).mark_bar(color=get_environment_color('에너지사용량')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='에너지사용량(kWh/㎡)', order='ascending')),
            y=alt.Y('에너지사용량(kWh/㎡):Q', title='에너지사용량 (kWh/㎡)'),
            tooltip=['회사:N', '에너지사용량(kWh/㎡):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 에너지사용량 비교 (낮을수록 좋음)"
        ).interactive()
        
        st.altair_chart(energy_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 건설폐기물 비교
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🗑️ 업체별 건설폐기물 비교")
        
        waste_chart = alt.Chart(data).mark_bar(color=get_environment_color('폐기물')).add_selection(
            alt.selection_point()
        ).encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='건설폐기물(ton)', order='ascending')),
            y=alt.Y('건설폐기물(ton):Q', title='건설폐기물 (ton)'),
            tooltip=['회사:N', '건설폐기물(ton):Q']
        ).properties(
            width='container',
            height=300,
            title="업체별 건설폐기물 비교 (낮을수록 좋음)"
        ).interactive()
        
        st.altair_chart(waste_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_ranking_analysis(data: pd.DataFrame):
    """종합 순위 분석"""
    
    # ESG 점수 계산
    scoring_data = calculate_esg_scores(data)
    
    # 종합 순위 섹션
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown("#### 🏆 ESG 종합 순위")
    
    # 순위를 컬럼으로 표시
    rank_cols = st.columns(min(len(scoring_data), 5))  # 최대 5개 컬럼
    
    for idx, row in scoring_data.iterrows():
        rank = idx + 1
        company = row['회사']
        total_score = row['종합점수']
        safety_score = row['안전점수']
        env_score = row['환경점수']
        
        with rank_cols[idx % len(rank_cols)]:
            if rank == 1:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #ffd700, #ffed4e); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥇 1위</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f}점</strong></p>
                    <small>안전: {safety_score:.1f} | 환경: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            elif rank == 2:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #c0c0c0, #e8e8e8); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥈 2위</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f}점</strong></p>
                    <small>안전: {safety_score:.1f} | 환경: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            elif rank == 3:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #cd7f32, #deb887); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>🥉 3위</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f}점</strong></p>
                    <small>안전: {safety_score:.1f} | 환경: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #f8f9fa, #e9ecef); border-radius: 10px; margin-bottom: 1rem;">
                    <h3>{rank}위</h3>
                    <h4>{company}</h4>
                    <p><strong>{total_score:.1f}점</strong></p>
                    <small>안전: {safety_score:.1f} | 환경: {env_score:.1f}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 간격 추가
    st.markdown("---")
    
    # 차트 섹션을 두 개의 행으로 분리
    col1, col2 = st.columns(2)
    
    with col1:
        # ESG 성과 비교 차트
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🎯 업체별 ESG 성과 비교")
        
        radar_data = prepare_radar_data(scoring_data)
        
        if not radar_data.empty:
            radar_chart = create_radar_chart(radar_data)
            st.altair_chart(radar_chart, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 업계 평균 대비 성과
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 📊 업계 평균 대비 성과")
        
        avg_score = scoring_data['종합점수'].mean()
        
        performance_chart = alt.Chart(scoring_data).mark_bar().encode(
            x=alt.X('회사:N', title='업체', sort=alt.EncodingSortField(field='종합점수', order='descending')),
            y=alt.Y('종합점수:Q', title='ESG 점수'),
            color=alt.condition(
                alt.datum.종합점수 > avg_score,
                alt.value(ESG_COLORS['status']['good']),   # 평균 이상: 녹색
                alt.value(ESG_COLORS['status']['danger'])  # 평균 이하: 빨간색
            ),
            tooltip=['회사:N', '종합점수:Q', '안전점수:Q', '환경점수:Q']
        ).properties(
            width='container',
            height=350,
            title=f"ESG 종합 점수 (업계 평균: {avg_score:.1f}점)"
        ).interactive()
        
        # 평균선 추가
        avg_line = alt.Chart(pd.DataFrame({'avg': [avg_score]})).mark_rule(
            color=ESG_COLORS['status']['warning'],
            strokeWidth=2,
            strokeDash=[5, 5]
        ).encode(y='avg:Q')
        
        combined_chart = performance_chart + avg_line
        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 추가 간격
    st.markdown("---")
    
    # 상세 점수 테이블
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 📋 상세 ESG 점수표")
    
    # 표시용 데이터프레임 생성
    display_df = scoring_data[['회사', '종합점수', '안전점수', '환경점수']].copy()
    display_df.columns = ['업체', 'ESG 종합점수', '안전 점수', '환경 점수']
    
    # 점수를 소수점 1자리로 포맷팅
    for col in ['ESG 종합점수', '안전 점수', '환경 점수']:
        display_df[col] = display_df[col].round(1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def calculate_esg_scores(data: pd.DataFrame) -> pd.DataFrame:
    """ESG 점수 계산"""
    
    scoring_data = data.copy()
    
    # 안전 점수 계산 (낮을수록 좋은 지표는 역산)
    scoring_data['사고율점수'] = 100 - (scoring_data['사고율(‰)'] / scoring_data['사고율(‰)'].max()) * 50
    scoring_data['사망자점수'] = 100 - (scoring_data['사망자수'] / max(scoring_data['사망자수'].max(), 1)) * 50
    scoring_data['안전감사점수'] = scoring_data['안전감사 준수율(%)']
    # 산재보험금 지표는 새로운 API에서 제거됨
    
    # 환경 점수 계산
    scoring_data['탄소배출점수'] = 100 - (scoring_data['탄소배출량(tCO₂e)'] / scoring_data['탄소배출량(tCO₂e)'].max()) * 50
    scoring_data['에너지점수'] = 100 - (scoring_data['에너지사용량(kWh/㎡)'] / scoring_data['에너지사용량(kWh/㎡)'].max()) * 50
    scoring_data['재생에너지점수'] = scoring_data['재생에너지비율(%)'] * 1.5  # 가중치 적용
    scoring_data['폐기물점수'] = 100 - (scoring_data['건설폐기물(ton)'] / scoring_data['건설폐기물(ton)'].max()) * 50
    scoring_data['재활용점수'] = scoring_data['재활용률(%)']
    
    # 카테고리별 평균 점수 (산재보험금 제거)
    scoring_data['안전점수'] = (
        scoring_data['사고율점수'] + scoring_data['사망자점수'] + 
        scoring_data['안전감사점수']
    ) / 3
    
    scoring_data['환경점수'] = (
        scoring_data['탄소배출점수'] + scoring_data['에너지점수'] + 
        scoring_data['재생에너지점수'] + scoring_data['폐기물점수'] + scoring_data['재활용점수']
    ) / 5
    
    # 종합 점수 (안전 40%, 환경 60%)
    scoring_data['종합점수'] = scoring_data['안전점수'] * 0.4 + scoring_data['환경점수'] * 0.6
    
    # 종합점수 기준으로 정렬
    scoring_data = scoring_data.sort_values('종합점수', ascending=False).reset_index(drop=True)
    
    return scoring_data

def prepare_radar_data(scoring_data: pd.DataFrame) -> pd.DataFrame:
    """레이더 차트용 데이터 준비"""
    
    radar_data = []
    
    categories = ['안전점수', '환경점수']
    
    for _, row in scoring_data.iterrows():
        company = row['회사']
        for category in categories:
            radar_data.append({
                '회사': company,
                '카테고리': category.replace('점수', ''),
                '점수': row[category]
            })
    
    return pd.DataFrame(radar_data)

def create_radar_chart(radar_data: pd.DataFrame):
    """ESG 성과 비교 차트 생성"""
    
    # 회사별 안전/환경 점수를 비교하는 그룹 바 차트
    chart = alt.Chart(radar_data).mark_bar().encode(
        x=alt.X('회사:N', title='업체'),
        y=alt.Y('점수:Q', title='점수 (0-100)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('카테고리:N', 
                       scale=alt.Scale(domain=['안전', '환경'], 
                                     range=[ESG_COLORS['status']['danger'], ESG_COLORS['status']['good']]),
                       legend=alt.Legend(title="ESG 영역")),
        xOffset=alt.XOffset('카테고리:N'),
        tooltip=['회사:N', '카테고리:N', '점수:Q']
    ).properties(
        width='container',
        height=350,
        title="업체별 안전 vs 환경 점수 비교"
    ).interactive()
    
    return chart

if __name__ == "__main__":
    main()
