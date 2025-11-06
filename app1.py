import streamlit as st

# Configure page layout
st.set_page_config(
        page_title="맛춤식",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

from streamlit.components.v1 import html
import streamlit.components.v1 as components

from app_user_info import run_user_info
# from app_pref import run_pref
from app_eda import run_eda
from app_ml import run_ml
from app_img import run_img

# Theme detection script
def detect_system_theme():
    theme_script = """
        <script>
        const darkThemeMq = window.matchMedia('(prefers-color-scheme: dark)');
        const theme = darkThemeMq.matches ? 'dark' : 'light';
        window.parent.postMessage(theme, '*');
        </script>
    """
    components.html(theme_script, height=0)

# Custom CSS for theme-aware styling
def apply_custom_css():
    custom_css = """
    <style>
        /* Light theme colors - Based on uizard template */
        :root {
            --background-color: #F8F9FA;
            --card-bg: #FFFFFF;
            --text-color: #2C3E50;
            --primary-color: #3498DB;
            --secondary-color: #2ECC71;
            --accent-color: #E74C3C;
            --border-color: #E5E9F2;
            --sidebar-bg: #FFFFFF;
            --button-hover: #2980B9;
        }
        
        /* Dark theme colors - Based on uizard template */
        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #1A1D21;
                --card-bg: #242A33;
                --text-color: #ECF0F1;
                --primary-color: #3498DB;
                --secondary-color: #27AE60;
                --accent-color: #E74C3C;
                --border-color: #2C3E50;
                --sidebar-bg: #242A33;
                --button-hover: #2980B9;
            }
        }
        
        /* Global styles */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #3498DB;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }
        
        .stButton > button:hover {
            background-color: #2980B9;
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
        }
        
        /* Active/Selected button styling */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
            transform: translateX(4px);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #ff8c42 0%, #ffa35c 100%);
            transform: translateX(6px);
            box-shadow: 0 6px 16px rgba(255, 107, 53, 0.5);
        }
        
        /* Card styling */
        .custom-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid var(--border-color);
            transition: transform 0.3s ease;
        }
        
        .custom-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        /* Input fields */
        .stTextInput > div > div {
            background-color: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            background-color: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Data tables */
        .stDataFrame {
            background-color: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            padding: 1rem;
        }
        
        /* Metrics */
        .stMetric {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid var(--border-color);
        }
        
        /* Plots */
        .stPlot {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid var(--border-color);
        }
        
        /* Tab navigation */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            margin: 0 0.25rem;
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background-color: var(--primary-color);
        }
        
        /* Custom divider */
        .divider {
            border-bottom: 1px solid var(--border-color);
            margin: 2rem 0;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def main():
    # Apply theme detection and custom CSS
    detect_system_theme()
    apply_custom_css()
    
    # Sidebar customization
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: var(--primary-color); font-size: 2rem;">🍽️ 맛춤식</h2>
            <p style="color: var(--text-color); font-size: 1rem;">AI 맞춤형 식단 관리</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        menu_icons = {
            "홈": "🏠",
            "사용자 정보 입력": "👤",
            "AI 맞춤 식단 설정": "🍱",
            "음식 영양 정보 보기": "📊",
            "AI 음식 영양 분석기": "🤖",
            # "내 맛 선호도 입력": "🌶️"
            
        }
        
        menu = list(menu_icons.keys())
        
        # Initialize choice with session state
        if 'menu_choice' not in st.session_state:
            st.session_state.menu_choice = "홈"
        
        choice = st.session_state.menu_choice
        
        # Create buttons for each menu item
        for item in menu:
            if st.sidebar.button(
                f"{menu_icons[item]} {item}",
                key=item,
                use_container_width=True,
                type="secondary" if item != choice else "primary"
            ):
                st.session_state.menu_choice = item
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style="position: fixed; bottom: 0; padding: 1rem; text-align: center;">
            <p style="color: var(--text-color); font-size: 0.8rem;">
                © 2025 맛춤식<br>
                AI 기반 맞춤형 식단 관리 시스템
            </p>
        </div>
        """, unsafe_allow_html=True)

    if "홈" in choice:
        # Header Section
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color); font-size: 3rem; margin-bottom: 1rem;">
                맛춤식에 오신 것을 환영합니다
            </h1>
            <p style="color: var(--text-color); font-size: 1.2rem; max-width: 800px; margin: 0 auto;">
                AI 기술을 활용한 맞춤형 식단 관리로 당신의 건강한 식생활을 설계해드립니다
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistics Section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--primary-color); font-size: 2.5rem; margin: 0;">500+</h3>
                <p style="margin: 0;">등록된 음식</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--accent-color); font-size: 2.5rem; margin: 0;">📷</h3>
                <p style="margin: 0;">AI 음식 사진 분석</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--primary-color); font-size: 2.5rem; margin: 0;">100%</h3>
                <p style="margin: 0;">AI 맞춤형 추천</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Features Section
        st.markdown("""
        <h2 style="text-align: center; margin: 2rem 0;">주요 기능</h2>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="custom-card">
                <div style="display: flex; align-items: start;">
                    <div style="background-color: var(--primary-color); color: white; padding: 1rem; border-radius: 12px; margin-right: 1rem;">
                        🎯
                    </div>
                    <div>
                        <h3 style="margin: 0;">AI 기반 식단 분석</h3>
                        <p>음식 사진만으로 정확한 영양 정보를 분석하고 칼로리를 계산해드립니다.</p>
                    </div>
                </div>
            </div>
            
            <div class="custom-card">
                <div style="display: flex; align-items: start;">
                    <div style="background-color: var(--secondary-color); color: white; padding: 1rem; border-radius: 12px; margin-right: 1rem;">
                        📊
                    </div>
                    <div>
                        <h3 style="margin: 0;">영양 정보 확인</h3>
                        <p>음식을 검색해 영양 정보를 확인 하실 수 있습니다.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            
            
            <div class="custom-card">
                <div style="display: flex; align-items: start;">
                    <div style="background-color: var(--primary-color); color: white; padding: 1rem; border-radius: 12px; margin-right: 1rem;">
                        🍱
                    </div>
                    <div>
                        <h3 style="margin: 0;">AI 맞춤 추천</h3>
                        <p>사용자의 건강 상태와 선호도를 고려한 맞춤형 식단을 제안합니다.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Call-to-Action Section
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">지금 바로 시작하세요</h2>
            <p style="color: var(--text-color); margin-bottom: 2rem;">
                사용자 정보를 입력하고 AI 기반의 맞춤형 식단 관리를 경험해보세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
            
    elif "사용자 정보" in choice:
        run_user_info()
    elif "식단 설정" in choice:
        run_ml()
    elif "영양 정보" in choice:
        run_eda()
    elif "분석기" in choice:
        run_img()
    # elif "맛 선호도" in choice:
        # run_pref()


if __name__ == "__main__":
    main()