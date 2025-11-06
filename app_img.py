import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
from sklearn.ensemble import GradientBoostingRegressor
import re
import joblib

# ============================================================
# 1. 환경 설정 및 헬퍼 함수
# ============================================================

def load_model():
    """Gemini AI 모델을 로드합니다."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        st.error("❌ Gemini API 키가 누락되었습니다. secrets.toml에 GEMINI_API_KEY를 추가하세요.")
        return None

def extract_number(text, keyword):
    """AI 응답 텍스트에서 특정 키워드의 숫자 값을 추출합니다."""
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
    """회귀 모델 로드 또는 자동 생성"""
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "food_calorie_model.pkl")

    # 모델이 없으면 자동 생성
    if not os.path.exists(model_path):
        st.warning("⚠️ 사전 학습된 모델이 없습니다. 새 모델을 학습 중입니다...")

        # 기본 학습 데이터 (샘플 구조)
        df = pd.DataFrame({
            "탄수화물(g)": [50, 100, 150, 200, 250],
            "단백질(g)": [10, 20, 30, 40, 50],
            "지방(g)": [5, 10, 15, 20, 25],
            "당류(g)": [5, 10, 20, 30, 40],
            "나트륨(mg)": [300, 500, 800, 1000, 1200],
            "열량(kcal)": [300, 500, 700, 900, 1100]
        })

        X = df[["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"]]
        y = df["열량(kcal)"]

        model = GradientBoostingRegressor(random_state=42)
        model.fit(X, y)
        joblib.dump(model, model_path)
        st.success("✅ 새 모델 학습 및 저장 완료!")
        return model

    # 기존 모델 로드 (호환성 예외처리)
    try:
        model = joblib.load(model_path)
    except (ValueError, ModuleNotFoundError) as e:
        st.warning("⚠️ 모델 파일이 호환되지 않아 새로 학습합니다.")
        os.remove(model_path)
        return load_regression_model()
    return model

# ============================================================
# 2. 메인 실행 함수
# ============================================================

def run_img():
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 음식 영양 분석기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                음식 사진을 업로드하고 (필요시 음식 이름을 입력하여) 영양 정보를 분석해드립니다
            </p>
        </div>
    """, unsafe_allow_html=True)

    regressor = load_regression_model()
    if regressor is None:
        st.stop()

    # 이미지 업로드 UI
    st.markdown("""
        <div class="custom-card">
            <h2>📸 음식 사진 업로드</h2>
            <p>분석할 음식의 사진을 업로드하세요.</p>
        </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader("", type=['jpg', 'jpeg', 'png', 'webp'])
    user_food_name = st.text_input("음식 이름 (선택 사항)", placeholder="예: 닭가슴살 샐러드")

    if not file:
        st.info("👆 사진을 업로드해주세요.")
        return

    image = Image.open(file)
    st.image(image, width=800)

    if st.button("🚀 AI 영양 분석 시작", type="primary"):
        model = load_model()
        if model is None:
            return

        with st.spinner("🤖 AI가 이미지를 분석 중입니다..."):
            prompt = f"""
            당신은 한국 음식 영양분석에 전문적인 영양 코치입니다.
            음식 사진을 보고 영양 성분을 1인분 기준으로 추정하세요.
            음식 이름: {user_food_name if user_food_name else "사진 속 음식"}
            """
            ex = model.generate_content([prompt, image])
            finish = ex.text.strip()

        # 결과 파싱
        kcal = extract_number(finish, "열량")
        carbo = extract_number(finish, "탄수화물")
        protein = extract_number(finish, "단백질")
        fat = extract_number(finish, "지방")
        sugar = extract_number(finish, "당류")
        sodium = extract_number(finish, "나트륨")

        # 보정 모델 사용
        if all(v is not None for v in [carbo, protein, fat, sugar, sodium]):
            new_data = pd.DataFrame([[carbo, protein, fat, sugar, sodium]],
                                    columns=["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"])
            corrected_kcal = regressor.predict(new_data)[0]
        else:
            corrected_kcal = None

        # 결과 표시
        st.markdown("### 📊 AI 분석 결과")
        st.write(finish)

        if corrected_kcal:
            st.success(f"✨ 보정된 칼로리 예측: **{corrected_kcal:.2f} kcal**")

# ============================================================
# 3. 앱 실행
# ============================================================

if __name__ == "__main__":
    st.set_page_config(page_title="AI 음식 영양 분석기", layout="wide")
    st.markdown("""
        <style>
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #FFC107;
            --accent-color: #E91E63;
            --text-color: #333;
            --card-bg: #f9f9f9;
            --border-color: #eee;
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
