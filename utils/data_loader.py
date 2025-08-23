"""
데이터 로딩 및 전처리 유틸리티 함수들
"""

import json
import pandas as pd
import streamlit as st
from typing import Dict, List, Any
import os

@st.cache_data(ttl=300, show_spinner="데이터 로딩 중...")
def load_data() -> Dict[str, Any]:
    """
    data.json 파일을 로드하고 캐시합니다.
    
    Returns:
        Dict: 로드된 데이터
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        st.error("데이터 파일 형식이 올바르지 않습니다.")
        return {}

def get_companies() -> List[str]:
    """
    사용 가능한 회사 목록을 반환합니다.
    
    Returns:
        List[str]: 회사명 리스트
    """
    data = load_data()
    return data.get('metadata', {}).get('companies', [])

def get_years() -> List[str]:
    """
    사용 가능한 연도 목록을 반환합니다.
    
    Returns:
        List[str]: 연도 리스트
    """
    data = load_data()
    return data.get('metadata', {}).get('years', [])

@st.cache_data(ttl=300)
def get_latest_year_data() -> pd.DataFrame:
    """
    최신 연도의 모든 회사 데이터를 DataFrame으로 반환합니다.
    
    Returns:
        pd.DataFrame: 최신 연도 데이터
    """
    data = load_data()
    companies = data.get('companies', {})
    years = get_years()
    
    if not years:
        return pd.DataFrame()
    
    latest_year = max(years)
    
    rows = []
    for company, company_data in companies.items():
        if latest_year in company_data:
            row = {'회사': company, '연도': latest_year}
            
            # 안전 지표
            safety_data = company_data[latest_year].get('safety', {})
            row.update({
                '사고율(‰)': safety_data.get('accident_rate', 0),
                '사망자수': safety_data.get('fatalities', 0),
                '안전감사 준수율(%)': safety_data.get('safety_audit_compliance', 0),
                '산재보험금(백만원)': safety_data.get('workers_compensation', 0)
            })
            
            # 환경 지표
            env_data = company_data[latest_year].get('environment', {})
            row.update({
                '탄소배출량(tCO₂e)': env_data.get('carbon_emissions', 0),
                '에너지사용량(kWh/㎡)': env_data.get('energy_usage', 0),
                '재생에너지비율(%)': env_data.get('renewable_energy_ratio', 0),
                '건설폐기물(ton)': env_data.get('construction_waste', 0),
                '재활용률(%)': env_data.get('recycling_rate', 0)
            })
            
            rows.append(row)
    
    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def get_company_trend_data(company: str) -> pd.DataFrame:
    """
    특정 회사의 연도별 트렌드 데이터를 반환합니다.
    
    Args:
        company (str): 회사명
        
    Returns:
        pd.DataFrame: 연도별 트렌드 데이터
    """
    data = load_data()
    companies = data.get('companies', {})
    
    if company not in companies:
        return pd.DataFrame()
    
    company_data = companies[company]
    rows = []
    
    for year, year_data in company_data.items():
        row = {'회사': company, '연도': year}
        
        # 안전 지표
        safety_data = year_data.get('safety', {})
        row.update({
            '사고율(‰)': safety_data.get('accident_rate', 0),
            '사망자수': safety_data.get('fatalities', 0),
            '안전감사 준수율(%)': safety_data.get('safety_audit_compliance', 0),
            '산재보험금(백만원)': safety_data.get('workers_compensation', 0)
        })
        
        # 환경 지표
        env_data = year_data.get('environment', {})
        row.update({
            '탄소배출량(tCO₂e)': env_data.get('carbon_emissions', 0),
            '에너지사용량(kWh/㎡)': env_data.get('energy_usage', 0),
            '재생에너지비율(%)': env_data.get('renewable_energy_ratio', 0),
            '건설폐기물(ton)': env_data.get('construction_waste', 0),
            '재활용률(%)': env_data.get('recycling_rate', 0)
        })
        
        rows.append(row)
    
    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def get_multi_company_data(companies: List[str], year: str = None) -> pd.DataFrame:
    """
    여러 회사의 데이터를 비교용으로 반환합니다.
    
    Args:
        companies (List[str]): 회사명 리스트
        year (str, optional): 특정 연도. None일 경우 최신 연도 사용
        
    Returns:
        pd.DataFrame: 다중 회사 비교 데이터
    """
    data = load_data()
    companies_data = data.get('companies', {})
    
    if year is None:
        years = get_years()
        year = max(years) if years else '2025'
    
    rows = []
    for company in companies:
        if company in companies_data and year in companies_data[company]:
            year_data = companies_data[company][year]
            row = {'회사': company, '연도': year}
            
            # 안전 지표
            safety_data = year_data.get('safety', {})
            row.update({
                '사고율(‰)': safety_data.get('accident_rate', 0),
                '사망자수': safety_data.get('fatalities', 0),
                '안전감사 준수율(%)': safety_data.get('safety_audit_compliance', 0),
                '산재보험금(백만원)': safety_data.get('workers_compensation', 0)
            })
            
            # 환경 지표
            env_data = year_data.get('environment', {})
            row.update({
                '탄소배출량(tCO₂e)': env_data.get('carbon_emissions', 0),
                '에너지사용량(kWh/㎡)': env_data.get('energy_usage', 0),
                '재생에너지비율(%)': env_data.get('renewable_energy_ratio', 0),
                '건설폐기물(ton)': env_data.get('construction_waste', 0),
                '재활용률(%)': env_data.get('recycling_rate', 0)
            })
            
            rows.append(row)
    
    return pd.DataFrame(rows)

def get_units() -> Dict[str, str]:
    """
    각 지표의 단위 정보를 반환합니다.
    
    Returns:
        Dict[str, str]: 지표별 단위 정보
    """
    data = load_data()
    return data.get('metadata', {}).get('units', {})

