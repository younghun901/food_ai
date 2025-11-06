import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
# GradientBoostingRegressor를 사용하도록 import
from sklearn.ensemble import GradientBoostingRegressor 
import re
import joblib

# =S=======================================================================
# 1. 환경 설정 및 헬퍼 함수
# =========================================================================



def load_model():
    """Gemini AI 모델을 로드합니다."""
    # API 키 로딩 로직 유지
    api_key=st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # --- [유지] ---
    # gemini-2.5-flash 모델 유지
    return genai.GenerativeModel("gemini-2.5-flash") 
    # --- [유지 끝] ---

def extract_number(text, keyword):
    """AI 응답 텍스트에서 특정 키워드의 숫자 값을 추출합니다."""
    # 숫자 앞에 공백이 없는 경우를 위해 정규식 수정
    pattern = rf"{keyword}.*?(\d+)"
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def extract_section(text, start, end_marker=None):
    """AI 응답 텍스트에서 특정 섹션의 내용을 추출합니다."""
    start_idx = text.find(start)
    if start_idx == -1:
        return ""
    start_idx += len(start)
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(text)
    else:
        end_idx = len(text)
    return text[start_idx:end_idx].strip()

def load_regression_model():
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "food_calorie_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError("사전 학습된 모델 파일(food_calorie_model.pkl)이 없습니다. 먼저 py에서 모델을 학습 및 저장하세요.")
    model = joblib.load(model_path)
    return model

# =========================================================================
# 2. 메인 실행 함수
# =========================================================================

def run_img():
    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 음식 영양 분석기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                음식 사진을 업로드하고 (필요시 음식 이름을 입력하여) 영양 정보를 분석해드립니다
            </p>
        </div>
    """, unsafe_allow_html=True)
    try:
        regressor = load_regression_model()     # 이 부분이 반드시 필요
    except FileNotFoundError as e:
        st.error(f"❌ {e}")
        return


    # 2. 파일 업로드 및 사용자 입력
    st.markdown("""
        <div class="custom-card">
            <h2>📸 음식 사진 업로드</h2>
            <p>분석하고 싶은 음식의 사진을 업로드해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("", type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])
    
    user_food_name = st.text_input(
        "음식 이름 (선택 사항)",
        placeholder="예: 닭가슴살 샐러드, 참치 김치찌개",
        help="사진 인식의 정확도를 높이기 위해 음식 이름을 직접 입력할 수 있습니다."
    )
    
    if not file:
        st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--primary-color);">👆 사진을 업로드해주세요</h3>
                <p>지원 형식: JPG, JPEG, PNG, gif, webp, bmp</p>
            </div>
        """, unsafe_allow_html=True)
        return
        
    # 이미지 표시
    image = Image.open(file)
    st.markdown("""
        <div class="custom-card">
            <h2>🖼️ 분석할 이미지</h2>
        </div>
    """, unsafe_allow_html=True)
    # --- [유지] ---
    # width=800 유지
    st.image(image, width=800) 
    # --- [유지 끝] ---

    # ⭐ 3. '분석 시작' 버튼과 AI 분석 로직
    if st.button("🚀 AI 영양 분석 시작", type="primary"):
        
        model = load_model()
        if model is None:
             # API 키 로드 오류 시 중단
             return

        with st.spinner("🤖 AI가 이미지를 분석 중입니다..."):
            
            food_clarification = ""
            if user_food_name:
                food_clarification = f"사용자가 입력한 음식 이름은 **'{user_food_name}'**입니다. AI는 이 정보를 최우선으로 고려하여 분석해야 합니다."
            
            # 개선된 AI 프롬프트
            prompt = f"""
            당신은 한국 음식 영양분석에 전문적인 헬스 트레이너이자 영양 코치입니다.
            음식 사진을 보고 영양 성분을 1인분 기준으로 추정하세요.
            
            {food_clarification}
            
            **[중요]**
            1. 사진에 보이는 음식의 종류(예: 밥, 닭가슴살, 김치)와 양(예: 밥 200g, 닭가슴살 100g)을 최대한 구체적으로 고려하여 분석을 수행해야 합니다.
            2. 음식의 일반적인 레시피를 바탕으로 현실적이고 정량적인 수치만 추정하세요.
            3. 추정된 영양소 값이 비현실적(예: 탄수화물 0g, 단백질 1000g)이지 않도록 주의하세요.

            반드시 아래 형식을 그대로 유지하고 한국어로 작성하세요.
            (모든 수치는 단위 포함 : kcal, g, mg)

            🍽 음식 이름:  
            🔥 영양정보 (1인분 기준)
            - 열량(kcal):  
            - 탄수화물(g):  
            - 단백질(g):  
            - 지방(g):  
            - 당류(g):
            - 나트륨(mg):

            💡 운동 후 섭취 시 장점:  
            ⚠️ 주의사항:

            출력은 위 형식 그대로, 문장과 숫자만 포함된 깔끔한 텍스트로 작성하세요.
            """
            
            ex = model.generate_content([
                    prompt, 
                    image
                ])
            finish = ex.text.strip()

            # 4. 결과 출력
            st.markdown("""
                <div class="custom-card">
                    <h2>🤖 AI 분석 결과</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # --- [수정 유지 1: 음식 이름만 추출] ---
            food_name_text = extract_section(finish, "🍽 음식 이름:", "🔥 영양정보 (1인분 기준)")
            
            # --- [음식 이름 출력 (깔끔한 디자인 유지)] ---
            st.markdown(f"""
                <div class="custom-card" style="background-color: var(--card-bg); padding: 1rem; text-align: center;">
                    <h2 style="margin: 0; color: var(--text-color); font-weight: 700;">{food_name_text}</h2>
                </div>
            """, unsafe_allow_html=True)
            # --- [수정 완료] ---


            # 영양소 값 추출
            kcal = extract_number(finish, "열량")
            carbo = extract_number(finish, "탄수화물")
            protein = extract_number(finish, "단백질")
            fat = extract_number(finish, "지방")
            sugar = extract_number(finish, "당류")
            sodium = extract_number(finish, "나트륨")

            # 영양소 카드 표시
            st.markdown("""
                <div class="custom-card">
                    <h2>📊 영양소 분석</h2>
                </div>
            """, unsafe_allow_html=True)

            # --- [수정 유지 2: 카드 간 수평/수직 간격 적용] ---
            cols = st.columns(3, gap="medium") 
            # --- [수정 유지 끝 2] ---
            
            nutrient_data = [
                {"name": "열량", "value": kcal, "unit": "kcal", "icon": "🔥", "color": "primary"},
                {"name": "탄수화물", "value": carbo, "unit": "g", "icon": "🌾", "color": "secondary"},
                {"name": "단백질", "value": protein, "unit": "g", "icon": "🥩", "color": "accent"},
                {"name": "지방", "value": fat, "unit": "g", "icon": "🥑", "color": "primary"},
                {"name": "당류", "value": sugar, "unit": "g", "icon": "🍯", "color": "secondary"},
                {"name": "나트륨", "value": sodium, "unit": "mg", "icon": "🧂", "color": "accent"}
            ]

            for i, nutrient in enumerate(nutrient_data):
                with cols[i % 3]:
                    # --- [수정 유지 3: 카드 간 수직 간격 적용] ---
                    st.markdown(f"""
                        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center; margin-bottom: 1rem;">
                            <h3 style="color: var(--{nutrient['color']}-color); margin: 0;">{nutrient['icon']} {nutrient['name']}</h3>
                            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{nutrient['value'] if nutrient['value'] is not None else 'N/A'} {nutrient['unit']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # --- [수정 유지 끝 3] ---

            # Gradient Boosting Model을 사용한 칼로리 보정
            if all(v is not None for v in [carbo, protein, fat, sugar, sodium]):
                new_data = pd.DataFrame([[carbo, protein, fat, sugar, sodium]], 
                                        columns=["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"])
                corrected_kcal = regressor.predict(new_data)[0]
                
                # 보정된 칼로리 결과 표시
                st.markdown(f"""
                    <div class="custom-card" style="background-color: var(--card-bg); padding: 1rem; text-align: center;">
                        <h3 style="color: var(--primary-color);">✨ 칼로리 추정</h3>
                        <p style="font-size: 1.2rem;">AI 추정 칼로리: {kcal} kcal</p>
                        <p style="font-size: 1.2rem;"><strong>영양 성분 기반 칼로리 추정: {corrected_kcal:.2f} kcal</strong></p>
                    </div>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("⚠️ 일부 영양성분이 누락되어 kcal 보정이 불가능합니다.")

            # --- [수정 시작: 장점과 주의사항 가독성 개선 (글꼴 크기, 줄 간격 조정)] ---

            # 1. 운동 후 섭취 시 장점 (제목과 내용 모두를 커스텀 카드 안에 포함)
            advantage_content = extract_section(finish, "💡 운동 후 섭취 시 장점:", "⚠️ 주의사항:")
            st.markdown(f"""
                <div class="custom-card">
                    <h3 style="margin-bottom: 0.5rem; color: var(--primary-color);">💪 운동 후 섭취 시 장점</h3>
                    <hr style="border-top: 1px solid var(--border-color); margin: 0.5rem 0 1rem 0;">
                    <p style="white-space: pre-wrap; font-size: 1.1rem; line-height: 1.6;">{advantage_content}</p>
                </div>
            """, unsafe_allow_html=True)

            # 2. 주의사항 (제목과 내용 모두를 커스텀 카드 안에 포함)
            precaution_content = extract_section(finish, "⚠️ 주의사항:")
            st.markdown(f"""
                <div class="custom-card">
                    <h3 style="margin-bottom: 0.5rem; color: var(--accent-color);">⚠️ 주의사항</h3>
                    <hr style="border-top: 1px solid var(--border-color); margin: 0.5rem 0 1rem 0;">
                    <p style="white-space: pre-wrap; font-size: 1.1rem; line-height: 1.6;">{precaution_content}</p>
                </div>
            """, unsafe_allow_html=True)
            # --- [수정 끝] ---

# 이 스크립트를 메인으로 실행할 때 run_img() 함수를 호출합니다.
if __name__ == "__main__":
    # Streamlit 앱의 기본 스타일링을 위한 더미 코드 (원본 코드에 없어서 추가)
    st.set_page_config(page_title="AI 영양 분석기", layout="wide")
    
    # 사용자 정의 CSS (원본 코드에 없어서 추가 - 카드 스타일을 위해)
    st.markdown("""
        <style>
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #FFC107;
            --accent-color: #E91E63;
            --text-color: #333333;
            --card-bg: #f9f9f9;
            --border-color: #eeeeee;
        }
        [data-theme="dark"] {
            --primary-color: #66BB6A;
            --secondary-color: #FFD54F;
            --accent-color: #F06292;
            --text-color: #FAFAFA;
            --card-bg: #2d2d2d;
            --border-color: #3d3d3d;
        }
        .custom-card {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    run_img()