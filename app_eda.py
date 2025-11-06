import streamlit as st
import pandas as pd
import plotly.express as px



def run_eda():
    df = pd.read_csv('./food1.csv')

    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">음식 영양 정보</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                음식을 검색하여 영양 정보를 확인 하실 수 있습니다
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.caption("※ 모든 수치는 100g 또는 100ml 기준입니다. 섭취량(g/ml)을 입력하면 자동으로 계산됩니다.")

    # 음식 선택 + 섭취량 입력
    col1, col2 = st.columns([3, 1])
    with col1:
        choice = st.selectbox("음식을 선택하세요", df["식품명"].unique())
    with col2:
        user_amount = st.number_input("섭취량 (g/ml)", min_value=1, max_value=1000, value=100, step=10)

    info = df[df["식품명"] == choice].iloc[0]
    ratio = user_amount / 100

    # 🔹 섭취량에 따른 영양값 계산
    adj_energy = info['에너지(kcal)'] * ratio
    adj_carb = info['탄수화물(g)'] * ratio
    adj_protein = info['단백질(g)'] * ratio
    adj_fat = info['지방(g)'] * ratio
    adj_sodium = info['나트륨(mg)'] * ratio if '나트륨(mg)' in info else None
    adj_sugar = info['당류(g)'] * ratio if '당류(g)' in info else None

    # 음식명 + 섭취량 표시
    st.markdown(f"## 🍽️ {choice} ({user_amount:.0f}g 기준)")

    # 🔹 4분할 카드 형태로 핵심 정보 표시
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("칼로리", f"{adj_energy:.0f} kcal")
    col2.metric("탄수화물", f"{adj_carb:.1f} g")
    col3.metric("단백질", f"{adj_protein:.1f} g")
    col4.metric("지방", f"{adj_fat:.1f} g")

    # 🔹 나트륨 / 당류 정보 (있는 경우만)
    if adj_sodium is not None or adj_sugar is not None:
        st.markdown("### 🧂 나트륨 · 당류 섭취량")

        rec_sodium = 2000  # 하루 권장 나트륨 (mg)
        rec_sugar = 50     # 하루 권장 당류 (g)

        sodium_ratio = (adj_sodium / rec_sodium * 100) if adj_sodium else 0
        sugar_ratio = (adj_sugar / rec_sugar * 100) if adj_sugar else 0

        col1, col2 = st.columns(2)
        if adj_sodium is not None:
            color = "🟢" if sodium_ratio < 30 else "🟠" if sodium_ratio < 70 else "🔴"
            col1.write(f"**나트륨:** {adj_sodium:.0f} mg ({sodium_ratio:.1f}% {color})")
        if adj_sugar is not None:
            color = "🟢" if sugar_ratio < 30 else "🟠" if sugar_ratio < 70 else "🔴"
            col2.write(f"**당류:** {adj_sugar:.1f} g ({sugar_ratio:.1f}% {color})")

    # 🔹 도넛 그래프 (기존 그대로 유지)
    st.markdown("### 🥗 영양소 비율")
    nutrients = ['탄수화물', '단백질', '지방']
    values = [adj_carb, adj_protein, adj_fat]
    colors = ['#2ECC71', '#3498DB', '#E74C3C']

    fig = px.pie(
        names=nutrients,
        values=values,
        color=nutrients,
        color_discrete_sequence=colors,
        hole=0.4,
        title=f"{choice}의 영양 비율 ({user_amount:.0f}g 기준)"
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05, 0.05, 0.05])
    fig.update_layout(legend_title="영양소", margin=dict(t=50, b=20, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    # 🔹 자동 피드백
    st.markdown("### 💬 식단 피드백")

    carb_ratio = adj_carb * 4 / adj_energy * 100 if adj_energy > 0 else 0
    protein_ratio = adj_protein * 4 / adj_energy * 100 if adj_energy > 0 else 0
    fat_ratio = adj_fat * 9 / adj_energy * 100 if adj_energy > 0 else 0

    feedback = []

    # 탄수화물 비율 피드백
    if carb_ratio > 60:
        feedback.append("🍚 탄수화물 비중이 높아요. 밥이나 빵류 섭취를 줄여보세요.")
    elif carb_ratio < 40:
        feedback.append("🍞 탄수화물 비중이 낮아요. 에너지를 충분히 섭취하세요.")
    else:
        feedback.append("✅ 탄수화물 비율이 적정합니다.")

    # 단백질 피드백
    if protein_ratio < 15:
        feedback.append("💪 단백질 섭취가 적습니다. 달걀, 닭가슴살, 두부를 추가해보세요.")
    elif protein_ratio > 25:
        feedback.append("🥩 단백질이 많아요. 탄수화물과의 균형을 확인해보세요.")
    else:
        feedback.append("✅ 단백질 섭취가 적당합니다.")

    # 지방 피드백
    if fat_ratio > 30:
        feedback.append("🍟 지방 섭취가 높아요. 튀김이나 가공식품을 줄이세요.")
    elif fat_ratio < 10:
        feedback.append("🥑 지방이 적어요. 견과류나 올리브유로 보충해보세요.")
    else:
        feedback.append("✅ 지방 섭취도 적정합니다.")

    # 나트륨, 당류 피드백
    if adj_sodium and adj_sodium > 1500:
        feedback.append("⚠️ 나트륨이 높아요. 짠 음식 섭취를 줄이세요.")
    if adj_sugar and adj_sugar > 30:
        feedback.append("⚠️ 당류가 많아요. 단 음료나 디저트는 자제하세요.")

    for fb in feedback:
        st.write(fb)
