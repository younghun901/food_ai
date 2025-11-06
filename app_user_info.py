import streamlit as st


# ============================================================================
# 1. 초기화 함수
# ============================================================================


def initialize_state():
    """
    앱이 처음 실행될 때 필요한 변수들을 준비합니다.
    이미 값이 있으면 건드리지 않고, 없을 때만 기본값을 설정합니다.
    """
    if 'user_height' not in st.session_state:
        st.session_state.user_height = 160
    
    if 'user_weight' not in st.session_state:
        st.session_state.user_weight = 60
    
    if 'user_age' not in st.session_state:
        st.session_state.user_age = 25
    
    if 'bmi_result' not in st.session_state:
        st.session_state.bmi_result = None
    
    if 'status_category' not in st.session_state:
        st.session_state.status_category = ""
    
    if 'action_message' not in st.session_state:
        st.session_state.action_message = ""
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'user_info'


def clear_results():
    """
    BMI 계산 결과만 지웁니다.
    사용자가 입력한 키, 몸무게, 나이는 그대로 유지됩니다.
    """
    st.session_state.bmi_result = None
    st.session_state.status_category = ""
    st.session_state.action_message = ""


# ============================================================================
# 2. 데이터 가져오기 함수
# ============================================================================

def get_user_data():
    """
    현재 저장된 사용자 데이터를 가져옵니다.
    다른 파일이나 함수에서 사용자 정보가 필요할 때 사용합니다.
    """
    try:
        if not all(key in st.session_state for key in ['user_height', 'user_weight', 'user_age', 'bmi_result']):
            initialize_state()
            return {
                'height': None,
                'weight': None,
                'age': None,
                'bmi': None
            }
        
        return {
            'height': st.session_state.user_height,
            'weight': st.session_state.user_weight,
            'age': st.session_state.user_age,
            'bmi': st.session_state.bmi_result
        }
    except Exception:
        return {
            'height': None,
            'weight': None,
            'age': None,
            'bmi': None
        }


# ============================================================================
# 3. BMI 기준표
# ============================================================================

def get_bmi_criteria(age):
    """
    나이에 따라 다른 BMI 기준을 알려줍니다.
    """
    if 20 <= age < 40:
        return {
            'age_group': '20~40대',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 22.9,
            'overweight_max': 24.9,
            'description': '일반적인 아시아 기준'
        }
    elif 40 <= age < 60:
        return {
            'age_group': '40~60대',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 23.4,
            'overweight_max': 25.4,
            'description': '중년 이후 약간 높은 BMI 권장'
        }
    elif age >= 60:
        return {
            'age_group': '60대 이상',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 24.9,
            'overweight_max': 27.4,
            'description': '노년층은 다소 비만 허용 범위 확대'
        }
    else:  # 20세 미만
        return {
            'age_group': '20세 미만',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 22.9,
            'overweight_max': 24.9,
            'description': '일반적인 아시아 기준 적용'
        }


# ============================================================================
# 4. 상태별 스타일 정의
# ============================================================================

def get_status_style(category):
    """
    BMI 상태에 따라 카드 스타일을 반환합니다.
    """
    styles = {
        'underweight': {
            'bg_color': '#E3F2FD',
            'border_color': '#2196F3',
            'icon': '📉',
            'title': '저체중',
            'color': '#1976D2'
        },
        'normal': {
            'bg_color': '#E8F5E9',
            'border_color': '#4CAF50',
            'icon': '✅',
            'title': '정상 체중',
            'color': '#388E3C'
        },
        'overweight': {
            'bg_color': '#FFF3E0',
            'border_color': '#FF9800',
            'icon': '⚠️',
            'title': '과체중',
            'color': '#F57C00'
        },
        'obese': {
            'bg_color': '#FFEBEE',
            'border_color': '#F44336',
            'icon': '🚨',
            'title': '비만',
            'color': '#D32F2F'
        }
    }
    return styles.get(category, styles['normal'])


# ============================================================================
# 5. BMI 계산 함수
# ============================================================================

def calculate_bmi():
    """
    사용자가 입력한 정보로 BMI를 계산합니다.
    """
    height = st.session_state.user_height
    weight = st.session_state.user_weight
    age = st.session_state.user_age
    
    # --- 입력값 검사 ---
    if not height or height < 140 or height > 250:
        st.error("키는 140cm ~ 250cm 사이로 입력해주세요.")
        clear_results()
        return
    
    if not weight or weight < 40 or weight > 200:
        st.error("몸무게는 40kg ~ 200kg 사이로 입력해주세요.")
        clear_results()
        return
    
    if not age or age < 1 or age > 100:
        st.error("나이는 1세 ~ 100세 사이로 입력해주세요.")
        clear_results()
        return
    
    # --- BMI 계산 ---
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    st.session_state.bmi_result = bmi
    
    # --- 나이에 맞는 BMI 기준 가져오기 ---
    criteria = get_bmi_criteria(age)
    
    # --- BMI 상태 판단 ---
    if bmi < criteria['underweight']:
        st.session_state.status_category = 'underweight'
    elif bmi < criteria['normal_max']:
        st.session_state.status_category = 'normal'
    elif bmi <= criteria['overweight_max']:
        st.session_state.status_category = 'overweight'
    else:
        st.session_state.status_category = 'obese'
    
    # --- 적정 체중 범위 계산 ---
    ideal_weight_min = criteria['normal_min'] * (height_m ** 2)
    ideal_weight_max = criteria['normal_max'] * (height_m ** 2)
    ideal_weight_mid = (ideal_weight_min + ideal_weight_max) / 2
    
    # --- 액션 메시지 생성 ---
    if st.session_state.status_category == 'underweight':
        weight_diff = ideal_weight_mid - weight
        st.session_state.action_message = f"""
        <div class="status-value" style="font-size: 2.5rem; font-weight: bold; margin: 1.5rem 0;">
            +{weight_diff:.1f}kg
        </div>
        <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.7;">증량이 필요합니다</div>
        """
    elif st.session_state.status_category == 'normal':
        st.session_state.action_message = f"""
        <div class="status-value" style="font-size: 2rem; font-weight: bold; margin: 1.5rem 0;">
            완벽합니다! 🎉
        </div>
        <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.7;">현재 체중을 유지하세요</div>
        """
    elif st.session_state.status_category == 'overweight':
        weight_diff = weight - ideal_weight_max
        st.session_state.action_message = f"""
        <div class="status-value" style="font-size: 2.5rem; font-weight: bold; margin: 1.5rem 0;">
            -{weight_diff:.1f}kg
        </div>
        <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.7;">감량을 권장합니다</div>
        """
    else:  # obese
        weight_diff = weight - ideal_weight_max
        st.session_state.action_message = f"""
        <div class="status-value" style="font-size: 2.5rem; font-weight: bold; margin: 1.5rem 0;">
            -{weight_diff:.1f}kg
        </div>
        <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.7;">감량이 필요합니다</div>
        """


# ============================================================================
# 6. 화면 구성 (메인 UI)
# ============================================================================

def run_user_info():
    """
    BMI 계산기 화면을 만듭니다.
    """
    initialize_state()
    
    if st.session_state.current_page != 'user_info':
        clear_results()
        st.session_state.current_page = 'user_info'
    
    # 커스텀 CSS
    custom_css = """
    <style>
    /* 입력 필드 스타일 */
    div[data-testid*="stNumberInput"] > div[data-baseweb="base-input"] {
        background: var(--card-bg); 
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 0.5rem 0.5rem;
    }

    div[data-testid*="stNumberInput"] input {
        font-size: 1.5rem !important;
        text-align: center;
        margin: 0.5rem 0;
        padding: 0 !important;
    }

    div[data-testid*="stNumberInput"] > label {
        text-align: center;
        padding-bottom: 0.5rem;
    }
    div[data-testid*="stNumberInput"] label p {
        color: var(--primary-color) !important;
        font-size: 1rem !important;
        font-weight: bold;
        margin: 0 !important;
    }
    
    div[data-baseweb="base-input"] > div:nth-child(2) {
        background: var(--card-bg);
    }
    
    /* 상태별 색상 - 라이트 테마 */
    .status-underweight {
        border: 3px solid #2196F3;
    }
    .status-underweight .status-icon { color: #2196F3; }
    .status-underweight .status-title { color: #1976D2; }
    .status-underweight .status-value { color: #1976D2; }
    
    .status-normal {
        border: 3px solid #4CAF50;
    }
    .status-normal .status-icon { color: #4CAF50; }
    .status-normal .status-title { color: #388E3C; }
    .status-normal .status-value { color: #388E3C; }
    
    .status-overweight {
        border: 3px solid #FF9800;
    }
    .status-overweight .status-icon { color: #FF9800; }
    .status-overweight .status-title { color: #F57C00; }
    .status-overweight .status-value { color: #F57C00; }
    
    .status-obese {
        border: 3px solid #F44336;
    }
    .status-obese .status-icon { color: #F44336; }
    .status-obese .status-title { color: #D32F2F; }
    .status-obese .status-value { color: #D32F2F; }
    
    /* 다크 테마일 때 */
    @media (prefers-color-scheme: dark) {
        .status-underweight .status-icon { color: #64B5F6; }
        .status-underweight .status-title { color: #64B5F6; }
        .status-underweight .status-value { color: #64B5F6; }
        
        .status-normal .status-icon { color: #81C784; }
        .status-normal .status-title { color: #81C784; }
        .status-normal .status-value { color: #81C784; }
        
        .status-overweight .status-icon { color: #FFB74D; }
        .status-overweight .status-title { color: #FFB74D; }
        .status-overweight .status-value { color: #FFB74D; }
        
        .status-obese .status-icon { color: #E57373; }
        .status-obese .status-title { color: #E57373; }
        .status-obese .status-value { color: #E57373; }
    }
    
    .info-box {
        margin-top: 1rem;
        padding: 1rem;
        background: var(--background-color);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    /* 결과 카드만 높이 통일 */
    .result-card {
        min-height: 280px;
        display: flex;
        flex-direction: column;
    }
    
    .result-card > div {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # --- 화면 제목 ---
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">BMI 계산기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                사용자의 정보를 입력받아 BMI를 계산하여 식단을 추천하는 데 활용됩니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    

    # --- 입력 섹션 ---
    st.markdown("""
        <div class="custom-card">
            <h2>👤 사용자 정보 입력</h2>
            <p>키, 몸무게, 나이를 입력해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 입력 필드 ---
    col1, col2, col3 = st.columns(3)

    with col1:
        height = st.number_input(
            '키(cm)', 
            min_value=140,
            max_value=250,
            step=1,
            value=st.session_state.user_height,
            help="키는 140cm ~ 250cm 사이로 입력해주세요",
            label_visibility="visible"
        )
        if height != st.session_state.user_height:
            st.session_state.user_height = height
            clear_results()
    
    with col2:
        weight = st.number_input(
            '몸무게(kg)', 
            min_value=40,
            max_value=200,
            step=1,
            value=st.session_state.user_weight,
            label_visibility="visible"
        )
        if weight != st.session_state.user_weight:
            st.session_state.user_weight = weight
            clear_results()
    
    with col3:
        age = st.number_input(
            '나이', 
            min_value=1,
            max_value=100,
            step=1,
            value=st.session_state.user_age,
            label_visibility="visible"
        )
        if age != st.session_state.user_age:
            st.session_state.user_age = age
            clear_results()
    
    # --- BMI 계산 버튼 ---
    st.button('BMI 계산 및 결과 확인', on_click=calculate_bmi, use_container_width=True)
    
    # --- 결과 표시 ---
    if st.session_state.bmi_result is not None:
        style = get_status_style(st.session_state.status_category)
        criteria = get_bmi_criteria(st.session_state.user_age)
        
        st.markdown("""
            <div class="custom-card">
                <h2 style="color: var(--primary-color);">BMI 계산 결과</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        # BMI 수치 카드 (왼쪽)
        with col1:
            st.markdown(f"""
            <div class="custom-card result-card">
                <div style="text-align: center;">
                    <h3 style="color: var(--accent-color); margin-bottom: 1rem;">📊 BMI 수치</h3>
                    <div class="status-value" style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">
                        {st.session_state.bmi_result:.1f}
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.7;">
                        정상 범위: {criteria['normal_min']} ~ {criteria['normal_max']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 상태 카드 (가운데)
        with col2:
            st.markdown(f"""
            <div class="custom-card result-card status-{st.session_state.status_category}">
                <div style="text-align: center;">
                    <div class="status-icon" style="font-size: 4rem; margin-bottom: 1rem;">{style['icon']}</div>
                    <div class="status-title" style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;">
                        {style['title']}
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-color); margin-top: 1rem; opacity: 0.7;">
                        {criteria['age_group']} 기준
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 액션 카드 (오른쪽)
        with col3:
            st.markdown(f"""
            <div class="custom-card result-card">
                <div style="text-align: center;">
                    <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">🎯 권장 사항</h3>
                    {st.session_state.action_message}
            """, unsafe_allow_html=True)
        
        # --- 다음 단계 버튼 ---
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        if st.button('🍱 AI 맞춤 식단 추천받기', key='goto_ml', use_container_width=True, type='primary'):
            st.session_state.menu_choice = 'AI 맞춤 식단 설정'
            st.rerun()