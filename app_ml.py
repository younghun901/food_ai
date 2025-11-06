import streamlit as st
import os
import google.generativeai as genai

# app_user_info 모듈에서 필요한 함수를 임포트합니다.
# get_bmi_criteria를 추가하여 나이별 기준을 사용할 수 있게 합니다.
from app_user_info import get_user_data, get_bmi_criteria 


# 제미나이 API 키 불러오기
api_key=st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')



def determine_bmi_status(bmi, age):
    """app_user_info.py의 나이별 기준에 따라 BMI 상태를 결정합니다."""
    if bmi is None or age is None:
        return "정보 없음"
    
    criteria = get_bmi_criteria(age)
    
    if bmi < criteria['underweight']:
        return "저체중"
    elif bmi < criteria['normal_max']:
        return "정상"
    elif bmi <= criteria['overweight_max']:
        return "과체중"
    else:
        return "비만"

# get_ai_diet_recommendation 함수에 age 매개변수 추가
def get_ai_diet_recommendation(bmi: float, age: int, preferences: list, avoid_foods: list) -> str:
    """AI를 통한 맞춤형 식단 추천"""
    
    # BMI 카테고리 결정: app_user_info의 age-specific 기준 사용
    bmi_category = determine_bmi_status(bmi, age)
    
    prompt = f"""
    다음 조건에 맞는 하루 식단을 추천해주세요:
    
    - BMI: {bmi:.1f} ({bmi_category})
    - 선호하는 음식: {', '.join(preferences) if preferences else '없음'}
    - 피해야 할 음식: {', '.join(avoid_foods) if avoid_foods else '없음'}
    
    다음 형식으로 자세히 응답해주세요:
    
    ### 🌅 아침
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 🌞 점심
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 🌙 저녁
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 💡 전체적인 식단 구성 이유:
    
    ### ⚠️ 주의사항:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"식단 생성 중 오류가 발생했습니다: {str(e)}"

def run_ml():
    
    
    # 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 맞춤 식단 설정</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                사용자 BMI 정보와 식단 선호도를 입력 하시면 맞춤 식단을 생성합니다
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # app_user_info에서 계산된 BMI 값과 나이 가져오기
    user_data = get_user_data()
    bmi = user_data.get('bmi')
    age = user_data.get('age') # 나이 정보도 가져와야 함
    
    # 사용자 정보 입력 섹션 (식단 선호도만 남김)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 사용자 BMI 정보")
        if bmi is None or age is None:
            # BMI 결과가 없을 경우 메시지 표시
            st.warning("⚠️ BMI 계산이 필요합니다. 'BMI 계산기' 페이지에서 키/몸무게/나이를 입력하고 계산해주세요.")
            bmi_status = "정보 없음"
        else:
            # app_user_info의 기준을 사용하여 상태 판단
            bmi_status = determine_bmi_status(bmi, age)
            criteria = get_bmi_criteria(age) # 나이별 기준표 가져오기
            
            st.metric(label="현재 BMI 수치", value=f"{bmi:.1f}", delta=bmi_status)
            
            # BMI 설명
            st.info(f"""
            **현재 BMI 상태:** **{bmi_status}**
            (나이: {user_data['age']}세, 키: {user_data['height']}cm, 몸무게: {user_data['weight']}kg 기준)
            
            💡 **{criteria['age_group']} 기준 범위:**
            - 정상: {criteria['normal_min']} ~ {criteria['normal_max']}
            - 과체중: {criteria['normal_max'] + 0.1:.1f} ~ {criteria['overweight_max']}
            """)

    
    with col2:
        st.markdown("### 🍳 식단 선호도")
        preferences = st.text_area(
            "선호하는 음식을 입력해주세요 (쉼표로 구분)",
            placeholder="예: 연어, 닭가슴살, 브로콜리",
            help="좋아하는 음식이나 자주 먹고 싶은 음식을 입력하세요."
        )
        
        avoid_foods = st.text_area(
            "피해야 할 음식을 입력해주세요 (쉼표로 구분)",
            placeholder="예: 땅콩, 우유, 새우",
            help="알레르기가 있거나 건강상 피해야 하는 음식을 입력하세요."
        )
        
        # 입력값 처리
        pref_list = [food.strip() for food in preferences.split(',') if food.strip()]
        avoid_list = [food.strip() for food in avoid_foods.split(',') if food.strip()]
    
    # 구분선
    st.divider()
    
    # 식단 생성 버튼
    if bmi is not None and age is not None:
        if st.button("🤖 AI 맞춤 식단 생성하기", type="primary"):
            with st.spinner("AI가 맞춤형 식단을 생성하고 있습니다..."):
                # age 정보도 get_ai_diet_recommendation에 전달
                recommendation = get_ai_diet_recommendation(bmi, age, pref_list, avoid_list)
                
                # 결과 표시
                st.markdown(recommendation)
                
                # 주의사항
                st.info("""
                💡 **참고사항**
                - 이 식단은 참고용이며, 실제 섭취 시에는 개인의 건강 상태를 고려해주세요.
                - 특별한 건강 상태나 질환이 있다면 반드시 의사와 상담 후 섭취하세요.
                - 식단은 매일 다양하게 구성하는 것이 좋습니다.
                """)
    else:
        # BMI나 나이 정보가 없을 때 버튼 대신 메시지 표시
        st.error("BMI 및 나이 정보가 없어 식단을 생성할 수 없습니다. 'BMI 계산기' 페이지에서 정보를 입력해 주세요.")


if __name__ == "__main__":
    run_ml()