"""
차트 스타일 및 색상 설정
ESG 테마 기반 색상 팔레트 (색맹 친화적)
"""

# ESG 테마 색상 팔레트
ESG_COLORS = {
    # 안전 지표 색상 (차분하고 경고성 있는 색상)
    'safety': {
        'accident_rate': '#DC3545',     # 사고율 - 빨간색
        'fatalities': '#FD7E14',        # 사망자수 - 주황색  
        'safety_compliance': '#28A745', # 안전감사 - 녹색
        'compensation': '#6F42C1'       # 산재보험금 - 보라색
    },
    
    # 환경 지표 색상 (자연 친화적 색상)
    'environment': {
        'carbon_emissions': '#DC3545',  # 탄소배출량 - 빨간색 (나쁨)
        'energy_usage': '#FFC107',      # 에너지사용량 - 노란색
        'renewable_energy': '#28A745',  # 재생에너지 - 녹색 (좋음)
        'waste': '#795548',             # 폐기물 - 갈색
        'recycling': '#17A2B8'          # 재활용률 - 청록색
    },
    
    # 회사별 구분 색상 (최대 5개)
    'companies': [
        '#007BFF',  # 파란색
        '#28A745',  # 녹색
        '#FFC107',  # 노란색
        '#DC3545',  # 빨간색
        '#6F42C1'   # 보라색
    ],
    
    # 상태 표시 색상
    'status': {
        'good': '#28A745',
        'warning': '#FFC107', 
        'danger': '#DC3545',
        'info': '#17A2B8'
    }
}

def get_safety_color(metric_key):
    """안전 지표에 따른 색상 반환"""
    color_mapping = {
        '사고율': 'accident_rate',
        '사망자수': 'fatalities', 
        '안전감사': 'safety_compliance',
        '산재보험금': 'compensation'
    }
    
    for key, color_key in color_mapping.items():
        if key in metric_key:
            return ESG_COLORS['safety'][color_key]
    
    return '#007BFF'  # 기본 색상

def get_environment_color(metric_key):
    """환경 지표에 따른 색상 반환"""
    color_mapping = {
        '탄소배출량': 'carbon_emissions',
        '에너지사용량': 'energy_usage',
        '재생에너지': 'renewable_energy',
        '폐기물': 'waste',
        '재활용률': 'recycling'
    }
    
    for key, color_key in color_mapping.items():
        if key in metric_key:
            return ESG_COLORS['environment'][color_key]
    
    return '#007BFF'  # 기본 색상

def get_company_color(index):
    """회사 인덱스에 따른 색상 반환"""
    return ESG_COLORS['companies'][index % len(ESG_COLORS['companies'])]
