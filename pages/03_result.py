# pages/03_result.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# check_session_timeout을 제거했으므로 더 이상 임포트하지 않습니다.
from utils import questions, calculate_score, classify_investment_type, show_footer, reset_survey_state

# --- 페이지 설정 ---
st.set_page_config(
    page_title="진단 결과",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 모든 페이지 공통 UI 숨김 CSS ---
st.markdown("""
    <style>
        /* 모든 페이지 공통: 헤더, 사이드바 내비게이션, 사이드바 컨트롤 버튼, 푸터 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: block; } /* 푸터는 이 페이지에서 다시 보이게 합니다. */

        /* `st.error`나 `st.warning` 등 메시지 컨테이너의 텍스트 색상 조정 (선택 사항) */
        div[data-testid="stAlert"] {
            color: initial; 
        }
    </style>
    """, unsafe_allow_html=True)


# --- 직접 접근 방지 로직 (로그인 여부 및 설문 완료 여부 확인) ---
# st.session_in -> st.session_state 오타 수정
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()


# 결과 페이지
def result_page():
    st.title("🎯 투자성향 진단 결과")
    st.markdown("---")

    total_score, score_breakdown = calculate_score(st.session_state.answers)
    investment_type, color = classify_investment_type(total_score)
    st.session_state.investment_type = investment_type # 대시보드 페이지에서 활용할 수 있도록 저장

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; border-radius: 15px; background-color: {color}20; border: 3px solid {color}; margin: 20px 0;">
            <h2 style="color: {color}; margin-bottom: 10px;">🎯 당신의 투자성향</h2>
            <h1 style="color: {color}; margin: 20px 0; font-size: 3em;">{investment_type}</h1>
            <h3 style="color: {color}; margin-top: 10px;">총점: {total_score:.1f}점</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    # --- ✨ 문항별 점수 분석 그래프 수정 부분 ✨ ---
    # 그래프에 표시할 짧은 문항 이름 리스트 (하드코딩)
    question_display_names = ["연령대", "투자기간", "투자경험", "지식수준", "자산비중", "수입원", "위험감수"]
    
    # score_breakdown에서 점수들을 question_display_names 순서에 맞춰 가져오기
    # questions.keys()의 순서와 question_display_names의 순서가 동일하다고 가정합니다.
    ordered_score_values = [score_breakdown[k] for k in questions.keys()]

    with col1:
        st.subheader("📈 문항별 점수 분석")
        df_scores = pd.DataFrame({
            '문항': question_display_names, # 짧은 문항 이름 사용
            '점수': ordered_score_values
        })
        fig_bar = px.bar(df_scores, x='문항', y='점수', color='점수', title="문항별 획득 점수", color_continuous_scale='Viridis')
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    # --- ✨ 여기까지 수정 ✨ ---

    with col2:
        st.subheader("🎯 투자성향 분포")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = total_score,
            domain = {'x': [0, 1], 'y': [0, 1]}, title = {'text': "투자성향 점수"},
            gauge = {
                'axis': {'range': [None, 100]}, 
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 20], 'color': "#4CAF50"}, {'range': [20, 40], 'color': "#8BC34A"},
                    {'range': [40, 60], 'color': "#FFC107"}, {'range': [60, 80], 'color': "#FF9800"},
                    {'range': [80, 100], 'color': "#F44336"}
                ],
            }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 투자성향별 특징")
    characteristics = {
        "안정형": {"설명": "원금 보전을 최우선", "추천상품": "예금, 국채", "위험수준": "매우 낮음", "기대수익": "낮음"},
        "안정추구형": {"설명": "안정성과 수익 조화", "추천상품": "우량회사채, 채권형펀드", "위험수준": "낮음", "기대수익": "보통"},
        "위험중립형": {"설명": "적정 위험 감수", "추천상품": "혼합형펀드, 일부 ELS", "위험수준": "보통", "기대수익": "보통"},
        "적극투자형": {"설명": "높은 수익 추구", "추천상품": "주식형펀드, ELS", "위험수준": "높음", "기대수익": "높음"},
        "공격투자형": {"설명": "최고 수익 목표", "추천상품": "파생상품, 레버리지펀드", "위험수준": "매우 높음", "기대수익": "매우 높음"},
    }
    char = characteristics[investment_type]

    st.info(f"**{investment_type} 특징:** {char['설명']}")
    st.success(f"**추천 투자상품:** {char['추천상품']}")

    st.markdown("---")

    if investment_type == "안정형":
        st.markdown("<h3 style='color: red; text-align: center;'>⚠️ 종목 추천 대상자가 아닙니다!</h3>", unsafe_allow_html=True)
        st.info("이 앱은 투자 상품 추천을 목적으로 하며, '안정형' 투자 성향에는 적합한 추천을 제공하지 않습니다.")
        st.markdown("---")

        col1 = st.columns(1)[0]
        with col1:
            if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True, type="primary"):
                st.session_state.reset_survey_flag = True
                st.switch_page("pages/01_questionnaire.py") # 설문 페이지로 리디렉션 경로 수정
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True):
                st.session_state.reset_survey_flag = True
                st.switch_page("pages/01_questionnaire.py") # 설문 페이지로 리디렉션 경로 수정
        with col2:
            if st.button("📈 위험 등급별 종목 대시보드 보기", type="primary", use_container_width=True):
                st.switch_page("pages/04_dashboard.py")

result_page()
show_footer()