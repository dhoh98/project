# pages/03_result.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
# complete_reset 함수는 더 이상 사용하지 않으므로 임포트에서 제외하거나 그대로 둬도 됩니다.
from utils import questions, calculate_score, classify_investment_type, show_footer

# 페이지 설정
st.set_page_config(
    page_title="진단 결과",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# 직접 접근 방지
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("app.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()


# 결과 페이지
def result_page():
    st.title("🎯 투자성향 진단 결과")
    st.markdown("---")

    total_score, score_breakdown = calculate_score(st.session_state.answers)
    investment_type, color = classify_investment_type(total_score)

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
    question_names = ["연령대", "투자기간", "투자경험", "지식수준", "자산비중", "수입원", "위험감수"]
    with col1:
        st.subheader("📈 문항별 점수 분석")
        df_scores = pd.DataFrame({
            '문항': question_names,
            '점수': list(score_breakdown.values())
        })
        fig_bar = px.bar(df_scores, x='문항', y='점수', color='점수', title="문항별 획득 점수", color_continuous_scale='Viridis')
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

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

    # --- <<< 버튼 수정 부분 >>> ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True):
            st.switch_page("app.py")

    with col2:
        # '새로운 진단 시작' 버튼을 '대시보드 보기'로 변경
        if st.button("📈 위험 등급별 종목 대시보드 보기", type="primary", use_container_width=True):
            # 세션 상태는 그대로 유지한 채, 대시보드 페이지로 이동합니다.
            st.switch_page("pages/04_dashboard.py")

result_page()
show_footer()