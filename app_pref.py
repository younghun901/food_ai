import pandas as pd
import streamlit as st

# ------------------- 상수 -------------------
DAILY_LIMITS = {"나트륨": 2000, "당류": 50}
SERVING_SIZE = 300  # 1인분 기준 (300g)

# ------------------- 피드백 함수 -------------------
def feedback(consumed, limit, nutrient):
    ratio = consumed / limit * 100
    if nutrient == "나트륨":
        msg = "👍 좋아요! 하루 권장량 내에 있어요." if ratio <= 100 else "⚠️ 짠 음식을 조금 줄여보세요."
        return f"나트륨 섭취량: {consumed:.0f}mg (하루 권장량의 {ratio:.0f}%)<br>→ {msg}"
    else:
        msg = "👍 좋아요! 하루 권장량 내에 있어요." if ratio <= 100 else "⚠️ 단 음식을 조금 줄여보세요."
        return f"당류 섭취량: {consumed:.0f}g (하루 권장량의 {ratio:.0f}%)<br>→ {msg}"

# ------------------- 분석 함수 -------------------
def analyze_foods():
    food_list = st.session_state.food_list
    if not food_list:
        st.warning("음식을 한 개 이상 선택해주세요.")
        return

    try:
        df = pd.read_csv('./food1.csv')
    except FileNotFoundError:
        st.error("❌ food1.csv 파일을 찾을 수 없습니다.")
        return

    # 숫자형 변환
    df["나트륨(mg)"] = pd.to_numeric(df["나트륨(mg)"], errors="coerce").fillna(0)
    df["당류(g)"] = pd.to_numeric(df["당류(g)"], errors="coerce").fillna(0)

    # 선택한 음식 필터링
    matched = (
        df[df["식품명"].isin(food_list)]
        .groupby("식품명", as_index=False)
        .agg({"나트륨(mg)": "mean", "당류(g)": "mean"})
    )

    if matched.empty:
        st.error("선택한 음식의 영양 정보를 찾을 수 없습니다.")
        return

    # ✅ 100g → 300g (1인분 기준 환산)
    matched["나트륨(1인분mg)"] = matched["나트륨(mg)"] * (SERVING_SIZE / 100)
    matched["당류(1인분g)"] = matched["당류(g)"] * (SERVING_SIZE / 100)
    matched = matched.round({"나트륨(1인분mg)": 1, "당류(1인분g)": 2})

    # ✅ 총 섭취량 계산 (1인분 단위 합계)
    total_na = matched["나트륨(1인분mg)"].sum()
    total_su = matched["당류(1인분g)"].sum()

    # ------------------- 결과 표시 -------------------
    st.markdown("""
    <div class="custom-card">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">📊 섭취 결과 요약</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="custom-card" style="height:100%;">
            <div style="text-align:center;">
                <h3 style="color: var(--accent-color); margin-bottom: 1rem;">🧂 나트륨 섭취</h3>
                <p style="font-size:1.2rem;">{feedback(total_na, DAILY_LIMITS["나트륨"], "나트륨")}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="custom-card" style="height:100%;">
            <div style="text-align:center;">
                <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">🍯 당류 섭취</h3>
                <p style="font-size:1.2rem;">{feedback(total_su, DAILY_LIMITS["당류"], "당류")}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------- 세부 데이터 표시 -------------------
    st.markdown("""
    <div class="custom-card" style="margin-top:2rem;">
        <h3 style="color: var(--primary-color);">🧾 선택한 음식의 영양 정보 (1인분 기준 300g)</h3>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        matched[["식품명", "나트륨(1인분mg)", "당류(1인분g)"]],
        use_container_width=True,
        hide_index=True
    )

# ------------------- 메인 UI -------------------
def run_pref():
    # ------------------- 스타일 -------------------
    st.markdown("""
    <style>
        div[data-testid="column"] > div { overflow-x: hidden; }
        div[data-testid="stDataFrame"] { width: 100% !important; }
        div[data-testid="stDataFrame"] > div { width: 100% !important; overflow-x: auto; }
        .custom-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # ------------------- 초기화 -------------------
    if "food_list" not in st.session_state:
        st.session_state.food_list = []

    # ------------------- 데이터 로드 -------------------
    try:
        df = pd.read_csv('./food1.csv')
        food_options = sorted(df["식품명"].dropna().unique().tolist())
    except FileNotFoundError:
        st.error("❌ food1.csv 파일을 찾을 수 없습니다.")
        return

    st.markdown("""
        <div style="text-align:center; padding:2rem 0;">
            <h1 style="color:var(--primary-color);">🍽️ 나트륨·당류 섭취 분석</h1>
            <p style="font-size:1.1rem;">아래에서 여러 음식을 선택해보세요.</p>
        </div>
    """, unsafe_allow_html=True)

    # ✅ 다중 선택 자동완성
    selected_foods = st.multiselect(
        "🍴 음식 검색 및 선택",
        options=food_options,
        default=st.session_state.food_list,
        key="multi_food"
    )

    # 선택된 음식 목록 업데이트
    st.session_state.food_list = selected_foods

    # ------------------- 선택 목록 표시 -------------------
    if st.session_state.food_list:
        st.markdown("#### 📝 현재 선택된 음식 목록")
        for food in st.session_state.food_list:
            st.markdown(f"- {food}")
        st.divider()
        st.button("섭취량 분석하기", on_click=analyze_foods, use_container_width=True)
    else:
        st.info("위의 검색창에서 여러 음식을 선택해보세요!")
