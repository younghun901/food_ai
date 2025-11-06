# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import os

# # --- 설정 및 데이터 로드 ---

# # 파일 경로: 'food.csv'가 현재 스크립트 파일과 같은 위치에 있다고 가정
# DATA_FILE = 'food.csv'

# # Streamlit 페이지 설정
# st.set_page_config(layout="wide", page_title="영양 밸런스 시각화")

# # 'food.csv' 파일이 존재하는지 확인하고 데이터 로드
# @st.cache_data(ttl=3600)  # 1시간 동안 캐시 유지
# def load_data():
#     if not os.path.exists(DATA_FILE):
#         st.error(f"⚠️ 파일 경로를 확인해주세요: '{DATA_FILE}' 파일을 찾을 수 없습니다.")
#         # 더미 데이터 생성 (테스트용)
#         data = {
#             '식품명': ['사과', '바나나', '닭가슴살', '현미밥', '고등어', '샐러드', '우유'],
#             '에너지(kcal)': [95, 105, 165, 205, 200, 150, 120],
#             '탄수화물(g)': [25, 27, 0, 45, 0, 10, 12],
#             '단백질(g)': [0.5, 1.3, 31, 4.5, 30, 15, 8],
#             '지방(g)': [0.3, 0.4, 3.6, 1.5, 10, 5, 5],
#             '식사_유형': ['아침', '아침', '점심', '점심', '저녁', '점심', '아침']
#         }
#         df = pd.DataFrame(data)
#         st.info("💡 'food.csv' 파일이 없어 테스트용 더미 데이터를 사용합니다. 실제 데이터를 넣어주세요.")
#         return df
    
#     # ----------------------------------------------------
#     # ⭐ 인코딩 오류 해결을 위해 'cp949' 또는 'euc-kr' 인코딩을 시도합니다.
#     # ----------------------------------------------------
#     try:
#         # 1. CP949 (ms949) 인코딩으로 시도
#         df = pd.read_csv(DATA_FILE, encoding='cp949') 
#         return df
#     except UnicodeDecodeError:
#         try:
#             # 2. euc-kr 인코딩으로 시도
#             df = pd.read_csv(DATA_FILE, encoding='euc-kr') 
#             return df
#         except Exception as e:
#             st.error(f"데이터 로드 중 오류 발생: 인코딩 문제 해결 실패. 오류: {e}")
#             return pd.DataFrame()
#     except Exception as e:
#         st.error(f"데이터 로드 중 오류 발생: {e}")
#         return pd.DataFrame()

# df = load_data()

# # --- 3.3 영양 밸런스 시각화 기능 ---
# st.title("🍎 3.3 영양 밸런스 시각화")
# st.subheader("선택된 음식, 목표 설정에 따른 영양소 비율 비교")

# # 사용자가 입력한 컬럼명
# FOOD_COL = '식품명'
# CALORIE_COL = '에너지(kcal)'
# NUTRITION_COLS = ['탄수화물(g)', '단백질(g)', '지방(g)']

# if df.empty:
#     st.warning("데이터가 없어 시각화를 진행할 수 없습니다. 'food.csv' 파일과 내용을 확인해 주세요.")
# else:
#     # 1. 데이터 필터링 모드 선택
    
#     # '전체 보기' 옵션을 제거합니다.
#     filter_mode = st.radio(
#         "데이터 필터링 모드를 선택하세요:",
#         ('개별 식품 조회', '목표 설정 및 비교'), 
#         horizontal=True
#     )

#     df_selected = df.copy()
#     selected_name = filter_mode # 시각화 제목에 사용할 이름
#     show_goal_comparison = False # 목표 비교 플래그
#     target_carbs_g, target_protein_g, target_fat_g = 0, 0, 0 # 목표 영양소 (g) 초기화

#     # ----------------------------------------------------
#     # ⭐ 모드별 필터링 로직 구현 및 목표 설정
#     # ----------------------------------------------------
    
#     # 개별 식품 조회 (음식 리스트)
#     if filter_mode == '개별 식품 조회' or filter_mode == '목표 설정 및 비교':
#         if FOOD_COL in df.columns:
#             all_foods = df[FOOD_COL].unique().tolist()
#             selected_foods = st.multiselect(
#                 "시각화할 식품을 선택하세요 (여러 개 선택 가능):",
#                 options=all_foods,
#                 default=[]
#             )
            
#             if selected_foods:
#                 df_selected = df[df[FOOD_COL].isin(selected_foods)].copy()
                
#                 # --- 선택된 식품 순서대로 데이터프레임 재정렬 ---
#                 df_selected[FOOD_COL] = pd.Categorical(
#                     df_selected[FOOD_COL], 
#                     categories=selected_foods, 
#                     ordered=True
#                 )
#                 df_selected = df_selected.sort_values(FOOD_COL)
#                 # ----------------------------------------------------------
                
#                 if len(selected_foods) > 3:
#                     display_foods = ", ".join(selected_foods[:3]) + f" 외 {len(selected_foods) - 3}개"
#                 else:
#                     display_foods = ", ".join(selected_foods)
                    
#                 selected_name = display_foods
#             else:
#                 # 선택된 식품이 없을 경우 빈 데이터프레임을 사용하고 경고 표시
#                 st.warning("시각화를 위해 식품을 선택해 주세요.")
#                 selected_name = '선택 없음'
#                 df_selected = pd.DataFrame(columns=df.columns) 
#         else:
#             st.error(f"데이터에 '{FOOD_COL}' 컬럼이 없어 식품 조회가 불가능합니다. 전체 데이터를 사용합니다.")
#             selected_name = '전체'
        
#         # 목표 설정 및 비교 모드 (개별 식품 조회 후 추가 입력)
#         if filter_mode == '목표 설정 및 비교':
#             show_goal_comparison = True
#             st.markdown("---")
#             st.subheader("🎯 개인 목표 설정 (BMI 및 탄/단/지 비율)")
            
#             # 선택된 식품이 있을 경우에만 목표 설정을 표시합니다.
#             if not df_selected.empty: 
#                 col_h, col_w = st.columns(2)
#                 height_cm = col_h.number_input("키 (cm):", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
#                 weight_kg = col_w.number_input("몸무게 (kg):", min_value=30.0, max_value=200.0, value=65.0, step=0.1)

#                 # BMI 계산
#                 height_m = height_cm / 100
#                 bmi = weight_kg / (height_m ** 2)
#                 st.metric("BMI (체질량지수)", f"{bmi:.2f}")

#                 st.markdown("---")
#                 st.markdown("**목표 영양소 비율 (%)**")

#                 # 목표 탄단지 비율 입력 (합계 100% 검증은 생략하고 단순 입력만 받음)
#                 col_c, col_p, col_f = st.columns(3)
#                 target_carbs_pct = col_c.slider("탄수화물(%)", min_value=20, max_value=70, value=50, step=5)
#                 target_protein_pct = col_p.slider("단백질(%)", min_value=10, max_value=50, value=30, step=5)
#                 target_fat_pct = col_f.slider("지방(%)", min_value=10, max_value=50, value=20, step=5)
                
#                 # 합계 확인 (사용자에게 피드백 제공)
#                 total_pct = target_carbs_pct + target_protein_pct + target_fat_pct
#                 if total_pct != 100:
#                     st.warning(f"⚠️ 목표 비율 합계가 100%가 아닙니다. 현재 합계: {total_pct}%")

#                 # 현재 선택된 음식의 총 칼로리를 '목표 칼로리'로 가정
#                 total_calories = df_selected[CALORIE_COL].sum() if CALORIE_COL in df_selected.columns else 0

#                 if total_calories > 0 and total_pct == 100:
#                     # 칼로리를 그램으로 변환 (탄/단: 4kcal/g, 지방: 9kcal/g)
#                     # 목표 칼로리(kcal) = 총 칼로리 * 목표 비율 (%)
                    
#                     target_carbs_kcal = total_calories * (target_carbs_pct / 100)
#                     target_protein_kcal = total_calories * (target_protein_pct / 100)
#                     target_fat_kcal = total_calories * (target_fat_pct / 100)

#                     target_carbs_g = target_carbs_kcal / 4
#                     target_protein_g = target_protein_kcal / 4
#                     target_fat_g = target_fat_kcal / 9
            
#             selected_name = f"{selected_name} - 목표 비교"

#     # '전체 보기' 모드 삭제로 인한 else if '전체 보기' 로직 제거
    
#     # 2. 필터링된 데이터 출력
#     st.markdown(f"**현재 시각화 대상 목록 ({selected_name}):**")
    
#     # 존재하는 컬럼만 선택하여 KeyError 방지
#     display_cols = [FOOD_COL, CALORIE_COL] + [col for col in NUTRITION_COLS if col in df_selected.columns]
#     valid_display_cols = [col for col in display_cols if col in df_selected.columns]
    
#     # --- 수정된 부분: .head(5) 제거하여 모든 행을 표시 ---
#     st.dataframe(df_selected[valid_display_cols], use_container_width=True)
#     # ----------------------------------------------------

#     st.markdown("---")
    
#     # 3. 영양소 총합 계산 및 시각화 준비
#     if df_selected.empty: # --- 선택된 식품이 없을 경우 시각화 건너뛰기
#         st.warning("선택된 식품이 없어 영양 밸런스 차트를 표시할 수 없습니다.")
#     elif not all(col in df_selected.columns for col in NUTRITION_COLS):
#         st.error(f"⚠️ 데이터프레임에 영양소 컬럼이 부족합니다. 필요한 컬럼: {NUTRITION_COLS}")
#     else:
#         # NaN 값은 0으로 처리하여 합산
#         total_nutrition = df_selected[NUTRITION_COLS].fillna(0).sum()
        
#         # 4. 데이터 시각화 (파이 차트 - 실제 섭취 비율)
#         st.subheader(f"📊 '{selected_name}' 영양 밸런스 (탄/단/지 비율)")
        
#         # Plotly를 사용한 파이 차트 생성 (비율 시각화에 적합)
#         fig = px.pie(
#             names=total_nutrition.index,  # 영양소 이름
#             values=total_nutrition.values,  # 총합 값
#             title=f"총 영양소 비율 ({selected_name})",
#             hole=.4,  # 도넛 형태로 만들기
#             color_discrete_sequence=px.colors.qualitative.Pastel # 색상 팔레트
#         )
        
#         # 차트 레이아웃 및 텍스트 설정
#         fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
#         fig.update_layout(legend_title_text="영양소", margin=dict(t=50, b=0, l=0, r=0))
        
#         # Streamlit에 차트 표시
#         st.plotly_chart(fig, use_container_width=True)
        
#         # 5. 추가 정보: 총 칼로리 및 상세 영양소
#         st.markdown("---")
#         st.subheader("총 영양소 및 칼로리 요약")
        
#         # 칼로리 컬럼이 존재하는 경우에만 합산
#         total_calories = df_selected[CALORIE_COL].sum() if CALORIE_COL in df_selected.columns else 0

#         col1, col2, col3 = st.columns([1, 2, 3])
        
#         with col1:
#             st.metric(label="총 칼로리", value=f"{total_calories:,.0f} kcal")
        
#         with col2:
#             # 총합 데이터프레임 요약본 표시
#             total_df_T = total_nutrition.to_frame(name="총합").T
#             total_df_T.index = ['총 영양소 합계 (g)']
#             st.dataframe(total_df_T, use_container_width=True)
            
#         with col3:
#             st.markdown(
#                 "**시각화 참고사항:**<br>"
#                 "표준적인 권장 비율은 탄수화물 50-60%, 단백질 20-30%, 지방 10-20% 정도입니다. (탄:단:지)", 
#                 unsafe_allow_html=True
#             )
        
#         # ----------------------------------------------------
#         # ⭐ 목표 vs 실제 섭취량 비교 막대 그래프 (추가된 부분)
#         # ----------------------------------------------------
#         if show_goal_comparison and total_calories > 0 and total_pct == 100:
#             st.markdown("---")
#             st.subheader("⚖️ 목표 영양소 vs 실제 섭취량 비교")

#             comparison_data = pd.DataFrame({
#                 '영양소': ['탄수화물(g)', '단백질(g)', '지방(g)'],
#                 '실제 섭취량 (g)': [total_nutrition['탄수화물(g)'], total_nutrition['단백질(g)'], total_nutrition['지방(g)']],
#                 '목표 섭취량 (g)': [target_carbs_g, target_protein_g, target_fat_g]
#             }).set_index('영양소')

#             # 막대 그래프 생성
#             fig_bar = go.Figure(data=[
#                 go.Bar(name='실제 섭취량', x=comparison_data.index, y=comparison_data['실제 섭취량 (g)'], marker_color='skyblue'),
#                 go.Bar(name='목표 섭취량', x=comparison_data.index, y=comparison_data['목표 섭취량 (g)'], marker_color='lightcoral')
#             ])

#             fig_bar.update_layout(
#                 barmode='group', 
#                 title='목표(g) 대비 실제 섭취량(g) 비교',
#                 yaxis_title='영양소 양 (g)',
#                 legend_title_text='구분'
#             )
#             st.plotly_chart(fig_bar, use_container_width=True)
            
#             st.success(f"✅ 목표 총 칼로리: {total_calories:,.0f} kcal에 대한 목표 영양소와 실제 섭취량을 비교했습니다.")
#         elif show_goal_comparison and total_pct != 100:
#              st.error("⚠️ 목표 영양소 비교를 위해 탄/단/지 비율의 합계를 100%로 설정해 주세요.")
