"""
ESG 건설업체 데이터 대시보드
메인 페이지
"""

import streamlit as st
import pandas as pd
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import (
    load_data, 
    get_companies, 
    get_years, 
    get_latest_year_data
)

# 페이지 설정
st.set_page_config(
    page_title="ESG 건설업체 대시보드",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
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
</style>
""", unsafe_allow_html=True)

def main():
    """메인 페이지 함수"""
    
    # 헤더
    st.markdown('<div class="main-header">🏗️ ESG 건설업체 데이터 대시보드</div>', 
                unsafe_allow_html=True)
    
    # 프로젝트 소개
    with st.container():
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 대시보드 소개
        이 대시보드는 주요 건설업체들의 **ESG(Environmental, Social, Governance)** 성과를 
        시각화하고 비교 분석할 수 있는 도구입니다.
        
        **📈 주요 기능:**
        - 연도별 ESG 지표 트렌드 분석
        - 업체별 성과 비교 및 벤치마킹
        - 안전 및 환경 지표 인터랙티브 시각화
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 모드 선택 섹션
    st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">📊 분석 모드 선택</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 연도별 비교 분석", use_container_width=True, type="primary"):
            st.session_state.analysis_mode = "year_comparison"
            st.rerun()
    
    with col2:
        if st.button("🏢 업체별 비교 분석", use_container_width=True, type="secondary"):
            st.session_state.analysis_mode = "company_comparison"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 현재 선택된 모드 표시 및 페이지 라우팅
    if 'analysis_mode' in st.session_state:
        if st.session_state.analysis_mode == "year_comparison":
            show_year_comparison_page()
        elif st.session_state.analysis_mode == "company_comparison":
            show_company_comparison_page()
    else:
        # 기본적으로 데이터 개요 표시
        show_data_overview()

def show_data_overview():
    """데이터 개요 페이지"""
    st.markdown("---")
    st.markdown('<div class="sub-header">📋 데이터 개요</div>', 
                unsafe_allow_html=True)
    
    # 기본 정보
    companies = get_companies()
    years = get_years()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("분석 대상 업체", f"{len(companies)}개 회사")
        
    with col2:
        st.metric("데이터 기간", f"{min(years)} - {max(years)}")
        
    with col3:
        st.metric("총 지표 수", "9개 ESG 지표")
    
    # 최신 연도 데이터 테이블
    st.markdown("### 📊 최신 연도 데이터 (2025년)")
    
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
            
            # CSV 다운로드 버튼
            csv_data = latest_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV로 다운로드",
                data=csv_data,
                file_name=f"ESG_데이터_{latest_data.iloc[0]['연도']}.csv",
                mime="text/csv"
            )
        else:
            st.warning("데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
    
    # 지표 설명
    with st.expander("📋 ESG 지표 설명"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔒 안전 지표**
            - **사고율(‰)**: 천 명당 산업재해 발생률
            - **사망자수**: 연간 작업장 내 사망자 수
            - **안전감사 준수율(%)**: 안전 규정 준수 비율
            - **산재보험금(백만원)**: 산업재해 보험금 지급액
            """)
        
        with col2:
            st.markdown("""
            **🌱 환경 지표**
            - **탄소배출량(tCO₂e)**: 연간 이산화탄소 배출량
            - **에너지사용량(kWh/㎡)**: 단위면적당 에너지 소비량
            - **재생에너지비율(%)**: 전체 에너지 중 재생에너지 비중
            - **건설폐기물(ton)**: 연간 건설폐기물 발생량
            - **재활용률(%)**: 폐기물 재활용 비율
            """)

def show_year_comparison_page():
    """연도별 비교 페이지로 리다이렉트"""
    st.switch_page("pages/yearReport.py")

def show_company_comparison_page():
    """업체별 비교 페이지로 리다이렉트"""
    st.switch_page("pages/companyReport.py")

if __name__ == "__main__":
    main()

