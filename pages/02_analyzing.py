import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
        /* 기본 Streamlit UI 요소 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: block; }
        
        /* 메인 컨테이너 스타일 */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 직접 접근 방지 로직 ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()

# KYC 관련 플래그는 이제 03_1_kyc_rule.py에서만 관리하면 됩니다.
# 여기서는 단순히 세션에 있는지 확인만 합니다.
if 'kyc_acknowledged_for_session' not in st.session_state:
    st.session_state.kyc_acknowledged_for_session = False


# 결과 페이지 메인 함수
def result_page():
    st.title("🎯 투자성향 진단 결과")
    st.markdown("---")

    total_score, score_breakdown = calculate_score(st.session_state.answers)
    investment_type, color = classify_investment_type(total_score)
    st.session_state.investment_type = investment_type

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
    
    # 문항별 점수 분석 그래프 (꺾은선 그래프)
    question_display_names = ["연령대", "투자기간", "투자경험", "지식수준", "자산비중", "수입원", "위험감수"]
    ordered_score_values = [score_breakdown[k] for k in questions.keys()]

    with col1:
        st.subheader("📈 문항별 점수 분석")
        df_scores = pd.DataFrame({
            '문항': question_display_names, 
            '점수': ordered_score_values
        })
        
        fig_line = px.line(
            df_scores, 
            x='문항', 
            y='점수', 
            title="문항별 획득 점수",
            markers=True, # 각 데이터 포인트에 마커 표시
            line_shape='linear', # 선 형태 ('linear'가 기본)
            labels={'문항': '설문 문항', '점수': '획득 점수'} # 축 레이블
        )
        
        # 꺾은선 색상 및 두께, 마커 스타일, 그리고 텍스트 표시 설정
        fig_line.update_traces(
            mode='lines+markers+text', # 선, 마커, 텍스트를 모두 표시
            text=df_scores['점수'], # 표시할 텍스트 데이터를 지정
            textposition='top center', # 텍스트를 마커 상단 중앙에 위치
            line=dict(color=color, width=3), # 선 색상과 두께 (투자성향 컬러 사용)
            marker=dict(size=10, color=color, line=dict(width=1, color='DarkSlateGrey')), # 마커 크기, 색상, 테두리
        )
        
        # y축 범위 설정 (0부터 최대 점수까지)
        max_score_possible_per_question = 0
        for q_key in questions:
            max_score_possible_per_question = max(max_score_possible_per_question, max(questions[q_key]['scores']))
        
        fig_line.update_yaxes(range=[0, max_score_possible_per_question * 1.1]) # 최대 점수보다 약간 높게

        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("🎯 투자성향 분포")
        
        # 1. 투자성향 범위, 한국어 레이블, 색상 정의
        # 점수 범위: 0~20, 20초과~40이하, 40초과~60이하, 60초과~80이하, 80초과
        score_categories = {
            "안정형":      {'range': [0, 20],   'label': '안정형',       'active_color': '#D0E0EE'}, # 연한 파랑
            "안정추구형": {'range': [20, 40],  'label': '안정<br>추구형', 'active_color': '#A6D0F0'},    # 중간 파랑
            "위험중립형": {'range': [40, 60],  'label': '위험<br>중립형', 'active_color': '#FFD870'},  # 노란색
            "적극투자형": {'range': [60, 80],  'label': '적극<br>투자형', 'active_color': '#A3E4D7'},   # 연한 녹색/민트
            "공격투자형": {'range': [80, 100], 'label': '공격<br>투자형', 'active_color': '#58D68D'}, # 진한 녹색
        }
        
        # 2. 게이지 스텝(단계) 및 활성 색상 설정
        gauge_steps_config = []
        inactive_segment_color = '#e0e0e0' # 비활성 구간의 기본 회색
        
        for key, data in score_categories.items():
            step_color = inactive_segment_color # 기본은 회색
            
            # total_score가 해당 범위에 속하면 활성 색상 적용
            # 명시된 점수 범위 규칙에 따라 조건 설정
            if (key == "안정형" and total_score <= 20) or \
               (key == "안정추구형" and total_score > 20 and total_score <= 40) or \
               (key == "위험중립형" and total_score > 40 and total_score <= 60) or \
               (key == "적극투자형" and total_score > 60 and total_score <= 80) or \
               (key == "공격투자형" and total_score > 80):
                step_color = data['active_color']
            
            gauge_steps_config.append({'range': data['range'], 'color': step_color})

        # 3. 게이지 차트 생성
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", # 게이지와 숫자 표시
            value = total_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            
            # 숫자(Score) 스타일링: CNN 지수처럼 크게 중앙 하단에
            number = {
                'suffix': '', # 숫자 뒤에 붙는 단위 없음
                'font': {'size': 55, 'color': 'black'}, # 숫자 폰트 크기 및 색상
                'valueformat': '.0f' # 정수로 표시
            },
            
            # 게이지 자체 스타일링
            gauge = {
                'shape': 'angular', # 반원형
                'axis': {
                    'range': [0, 100], 
                    'tickmode': 'array',
                    'tickvals': [0, 25, 50, 75, 100], # 눈금 값
                    'ticktext': ['0', '25', '50', '75', '100'], # 눈금 텍스트
                    'showticklabels': True,
                    'ticks': 'outside', # 눈금을 게이지 바깥쪽에 표시
                    'tickwidth': 1,
                    'ticklen': 8, # 눈금 길이
                    'tickcolor': 'gray',
                }, 
                'bar': {'color': 'black', 'thickness': 0.8}, # 바늘 색상 (검정), 두께
                'bgcolor': 'white', # 게이지 배경색 (CNN 지수처럼 흰색)
                'steps': gauge_steps_config, # 동적으로 설정된 스텝들
            }
        ))
        
        # 4. 게이지 상단에 "투자성향 분포" 제목 및 현재 성향 레이블 추가
        # Plotly의 annotations를 사용하여 한국어 레이블을 배치하고 색상도 동적으로 적용
        fig_gauge.update_layout(
            height=400, 
            margin=dict(l=20, r=20, t=100, b=20), # 상단 마진을 늘려 제목 공간 확보
            font_color="black", # 차트 기본 폰트 색상
            annotations=[
                # 안정형 (0-20)
                dict(
                    x=0.07, y=0.5, # 0에 가까운 위치
                    xref="paper", yref="paper",
                    text=score_categories["안정형"]['label'],
                    showarrow=False,
                    font=dict(size=14, color=score_categories["안정형"]['active_color'] if total_score <= 20 else inactive_segment_color),
                    textangle=45 # 텍스트 회전
                ),
                # 안정추구형 (20초과~40이하)
                dict(
                    x=0.25, y=0.8, # 25 근처 위치
                    xref="paper", yref="paper",
                    text=score_categories["안정추구형"]['label'],
                    showarrow=False,
                    font=dict(size=14, color=score_categories["안정추구형"]['active_color'] if total_score > 20 and total_score <= 40 else inactive_segment_color),
                    textangle=20 # 텍스트 회전
                ),
                # 위험중립형 (40초과~60이하)
                dict(
                    x=0.5, y=0.9, # 50 근처 위치 (가장 위)
                    xref="paper", yref="paper",
                    text=score_categories["위험중립형"]['label'],
                    showarrow=False,
                    font=dict(size=14, color=score_categories["위험중립형"]['active_color'] if total_score > 40 and total_score <= 60 else inactive_segment_color),
                    textangle=0 # 텍스트 회전 없음
                ),
                # 적극투자형 (60초과~80이하)
                dict(
                    x=0.75, y=0.8, # 75 근처 위치
                    xref="paper", yref="paper",
                    text=score_categories["적극투자형"]['label'],
                    showarrow=False,
                    font=dict(size=14, color=score_categories["적극투자형"]['active_color'] if total_score > 60 and total_score <= 80 else inactive_segment_color),
                    textangle=-20 # 텍스트 회전
                ),
                # 공격투자형 (80초과)
                dict(
                    x=0.93, y=0.5, # 100에 가까운 위치
                    xref="paper", yref="paper",
                    text=score_categories["공격투자형"]['label'],
                    showarrow=False,
                    font=dict(size=14, color=score_categories["공격투자형"]['active_color'] if total_score > 80 else inactive_segment_color),
                    textangle=-45 # 텍스트 회전
                ),
                # 메인 타이틀
                dict(
                    x=0.5, y=1.05, # 차트 상단 중앙에 위치
                    xref="paper", yref="paper",
                    text='<b>투자성향 분포</b>', # 볼드 처리
                    showarrow=False,
                    font=dict(size=24, color="black"),
                    align="center",
                )
            ]
        )
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
                st.switch_page("pages/01_questionnaire.py") 
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True):
                st.session_state.reset_survey_flag = True
                st.switch_page("pages/01_questionnaire.py") 
        
        with col2:
            # KYC 이미 확인했으면 바로 대시보드로
            if st.session_state.kyc_acknowledged_for_session:
                if st.button("📈 위험 등급별 종목 대시보드 보기", type="primary", use_container_width=True):
                    st.switch_page("pages/04_dashboard.py")
            else:
                # 03_1_kyc_rule.py 페이지로 이동
                if st.button("📈 위험 등급별 종목 대시보드 보기", type="primary", use_container_width=True):
                    st.switch_page("pages/03_1_kyc_rule.py")

# 메인 실행
result_page()
show_footer()