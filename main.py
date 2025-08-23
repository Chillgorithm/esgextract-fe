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
    """메인 페이지 함수"""
    
    # 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem;">
            ESGExtract
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0; font-weight: 300;">
            건설업체 ESG 데이터 대시보드
        </p>
    </div>
    """, unsafe_allow_html=True)
    

    
    # 모드 선택 섹션
    st.markdown('### 📊 분석 모드 선택')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 연도별 비교 분석", use_container_width=True, type="secondary"):
            st.session_state.analysis_mode = "year_comparison"
            st.rerun()
    
    with col2:
        if st.button("🏢 업체별 비교 분석", use_container_width=True, type="secondary"):
            st.session_state.analysis_mode = "company_comparison"
            st.rerun()
    
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
    st.markdown('### 📋 데이터 개요')
    
    # 기본 정보
    companies = get_companies()
    years = get_years()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(companies)}개</div>
            <div class="metric-label">분석 대상 업체</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{min(years)} - {max(years)}</div>
            <div class="metric-label">데이터 기간</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">9개</div>
            <div class="metric-label">ESG 지표</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 구분선과 간격
    st.markdown("---")
    
    # 최신 연도 데이터 테이블
    st.markdown("### 📊 최신 연도 데이터 (2025년)")
    
    with st.spinner("📊 데이터를 불러오는 중..."):
        try:
            # 프로그레스 바 표시
            progress_placeholder = st.empty()
            progress_placeholder.markdown("""
            <div class="progress-container">
                <div class="progress-bar" style="width: 100%;"></div>
            </div>
            <div class="loading-text">ESG 데이터 로딩 중...</div>
            """, unsafe_allow_html=True)
            
            latest_data = get_latest_year_data()
            progress_placeholder.empty()  # 프로그레스 바 제거
            
            if not latest_data.empty:
                # 데이터 포맷팅
                formatted_data = latest_data.copy()
            
                # 수치 컬럼 포맷팅
                numeric_columns = [
                    '사고율(‰)', '사망자수', '안전감사 준수율(%)', '재생에너지량(GWh)',
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
    
    # 사용법 가이드
    with st.expander("🆘 사용법 가이드"):
        st.markdown("""
        ### 📚 **대시보드 사용 방법**
        
        #### 🏠 **메인 페이지** (현재 페이지)
        - **최신 데이터 확인**: 2025년 모든 회사의 ESG 지표를 한눈에 확인
        - **CSV 다운로드**: 표 아래 다운로드 버튼으로 데이터 내보내기
        
        #### 📈 **연도별 비교 모드**
        1. 사이드바에서 **분석할 회사** 선택
        2. **연도 범위** 선택 (슬라이더 사용)
        3. **안전 지표** 탭에서 사고율, 사망자수, 안전감사 준수율, 산재보험금 추이 확인
        4. **환경 지표** 탭에서 탄소배출량, 에너지사용량, 재생에너지비율, 재활용률 추이 확인
        
        #### 🏢 **업체별 비교 모드**
        1. 사이드바에서 **비교할 회사들** 선택 (최대 5개)
        2. **안전 지표** 탭에서 회사간 안전 성과 비교
        3. **환경 지표** 탭에서 회사간 환경 성과 비교
        4. **순위 분석** 탭에서 종합 ESG 점수 및 레이더 차트 확인
        
        #### 💡 **팁**
        - 차트 위에 마우스를 올리면 **상세 데이터** 확인 가능
        - 차트를 **확대/축소**하려면 마우스 휠 사용
        - 모바일에서도 **터치**로 차트 조작 가능
        - **CSV 다운로드**로 추가 분석용 데이터 확보 가능
        
        #### ⌨️ **키보드 단축키**
        - **F5**: 페이지 새로고침
        - **Ctrl/Cmd + D**: CSV 다운로드 (해당 페이지에서)
        - **Esc**: 확장된 섹션 닫기
        - **Tab**: 다음 요소로 이동
        - **Shift + Tab**: 이전 요소로 이동
        """)
        
    # 키보드 단축키 스크립트
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
    
    with st.expander("📋 ESG 지표 설명"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔒 안전 지표**
            - **사고율(‰)**: 천 명당 산업재해 발생률
            - **사망자수**: 연간 작업장 내 사망자 수
            - **안전감사 준수율(%)**: 안전 규정 준수 비율
            """)
        
        with col2:
            st.markdown("""
            **🌱 환경 지표**
            - **탄소배출량(tCO₂e)**: 연간 이산화탄소 배출량
            - **에너지사용량(kWh/㎡)**: 단위면적당 에너지 소비량
            - **재생에너지비율(%)**: 전체 에너지 중 재생에너지 비중
            - **재생에너지량(GWh)**: 재생에너지 절대량
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

