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

        /* Plotly 차트 배경을 투명하게 (선택 사항) */
        .js-plotly-plot .plotly .main-svg {
            background-color: transparent !important;
        }

        /* st.info/st.success (stAlert) 내부 텍스트 및 컨테이너 크기 조정 */
        div[data-testid="stAlert"] {
            padding: 1.5em; /* 박스 내부 패딩 증가로 높이 키움 */
            min-height: 100px; /* 최소 높이 설정 (원하는 만큼 조절) */
        }
        div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
            font-size: 1.25em !important; /* 글자 크기 더 증가 (1.15 -> 1.25) */
            line-height: 1.8 !important; /* 줄 간격 더 넓게 */
            margin-bottom: 0 !important; /* 하단 마진 제거 */
        }
        /* Subheader 글자 크기 조정 */
        h3 {
            font-size: 1.7em !important; /* Subheader 크기 증가 (1.6 -> 1.7) */
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
    
    # --- ✨ 문항별 점수 분석과 투자성향별 점수 분포를 좌우 컬럼에 배치 ✨ ---
    col_chart, col_propensity_chart = st.columns([0.5, 0.5]) 

    with col_chart: # 왼쪽 컬럼: 문항별 획득 점수 (꺾은선 그래프)
        st.subheader("🎯 문항별 획득 점수") 
        question_display_names = ["연령대", "투자기간", "투자경험", "지식수준", "자산비중", "수입원", "위험감수"]
        ordered_score_values = [score_breakdown[k] for k in questions.keys()]

        df_scores = pd.DataFrame({
            '문항': question_display_names, 
            '점수': ordered_score_values
        })
        
        fig_line = px.line(
            df_scores, 
            x='문항', 
            y='점수', 
            title="문항별 획득 점수", 
            markers=True, 
            line_shape='linear', 
            labels={'문항': '', '점수': '획득 점수'} 
        )
        
        fig_line.update_traces(
            mode='lines+markers+text', 
            text=df_scores['점수'], 
            textposition='top center', 
            line=dict(color=color, width=3), 
            marker=dict(size=14, color=color, line=dict(width=1.5, color='DarkSlateGrey')), 
            textfont=dict(size=18, color='black') # 점수 숫자 폰트 크기
        )
        
        # y축 범위 설정 (-10부터 최대 점수까지)
        min_score_possible_per_question = -10 
        max_score_possible_per_question = 0
        for q_key in questions:
            max_score_possible_per_question = max(max_score_possible_per_question, max(questions[q_key]['scores']))
        
        fig_line.update_yaxes(
            range=[min_score_possible_per_question, max_score_possible_per_question * 1.1], 
            tickvals=[min_score_possible_per_question, 0, 5, 10, 15, 20], # 눈금 조정
            ticktext=[f'{min_score_possible_per_question}', '0', '5', '10', '15', '20'], # 눈금 텍스트 조정
            title_font=dict(size=18), # Y축 제목 "획득 점수" 폰트 크기
            tickfont=dict(size=16) # Y축 숫자 폰트 크기
        ) 

        fig_line.update_layout(
            height=400,
            xaxis=dict(
                tickfont=dict(size=18) # X축 변수(문항 이름) 폰트 크기
            ),
        )
        st.plotly_chart(fig_line, use_container_width=True) 

    with col_propensity_chart: # 오른쪽 컬럼: 투자성향 점수 분포 (가로 막대 그래프)
        st.subheader("🎯 투자성향 점수 분포") 

        propensity_data = [
            {"유형": "공격투자형", "최저점": 80, "최고점": 100, "점수범위": "80점 초과"},
            {"유형": "적극투자형", "최저점": 60, "최고점": 80, "점수범위": "60점 초과~80점 이하"},
            {"유형": "위험중립형", "최저점": 40, "최고점": 60, "점수범위": "40점 초과~60점 이하"},
            {"유형": "안정추구형", "최저점": 20, "최고점": 40, "점수범위": "20점 초과~40점 이하"},
            {"유형": "안정형", "최저점": 0, "최고점": 20, "점수범위": "20점 이하"}
        ]
        df_propensity_chart = pd.DataFrame(propensity_data)

        # '유형'을 역순으로 정렬하여 그래프에서 '안정형'이 아래쪽에 오도록
        df_propensity_chart['유형_정렬'] = pd.Categorical(df_propensity_chart['유형'], categories=[d['유형'] for d in propensity_data[::-1]], ordered=True)
        df_propensity_chart = df_propensity_chart.sort_values('유형_정렬')

        # 각 막대의 색상을 조건부로 설정 (하이라이트 로직)
        bar_colors = []
        inactive_bar_color = '#e0e0e0' # 비활성화된 막대의 색상
        for index, row in df_propensity_chart.iterrows():
            if row['유형'] == investment_type:
                bar_colors.append(color) # 현재 사용자의 투자성향 컬러 (main color)
            else:
                bar_colors.append(inactive_bar_color) # 나머지는 연한 회색
        
        fig_propensity = px.bar(
            df_propensity_chart, 
            x='최고점', 
            y='유형_정렬', 
            orientation='h', 
            title="", 
            text='점수범위', 
            color=bar_colors, # 동적으로 생성된 색상 리스트 사용
            color_discrete_map="identity", # 색상 리스트를 그대로 사용하도록 지시
            labels={'최고점': '점수', '유형_정렬': '투자성향'},
            hover_data={'점수범위': True, '유형': True, '최저점': True, '최고점': True, '유형_정렬': False} 
        )
        
        # x축 범위와 눈금 설정 (0부터 100까지)
        fig_propensity.update_xaxes(
            range=[0, 100], 
            tickvals=[0, 20, 40, 60, 80, 100], 
            ticktext=['0', '20', '40', '60', '80', '100점'],
            title_text="점수",
            tickfont=dict(size=18), # x축 눈금 폰트 크기
            title_font=dict(size=20) # x축 제목 "점수" 폰트 크기
        )
        # y축 제목 제거 및 눈금 폰트 크기 증가
        fig_propensity.update_yaxes(
            title_text="", 
            showgrid=False,
            tickfont=dict(size=20) # y축(유형) 눈금 폰트 크기
        )

        # 막대 내부 텍스트 스타일 (글자 크기 증가)
        fig_propensity.update_traces(
            texttemplate='%{text}', 
            textposition='inside', 
            insidetextanchor='middle', 
            marker_line_width=0, 
            textfont=dict(size=20, color='black') # 막대 내부 텍스트 폰트 크기
        )

        # 레이아웃 조정
        fig_propensity.update_layout(
            height=400, 
            showlegend=False, 
            yaxis={'categoryorder':'array', 'categoryarray': [d['유형'] for d in propensity_data[::-1]]} 
        )
        st.plotly_chart(fig_propensity, use_container_width=True)
    # --- ✨ 여기까지 수정 ✨ ---

    st.markdown("---")
    st.subheader("💡 투자성향별 특징")
    # --- ✨ 투자성향별 특징 텍스트 및 글자 크기 조정 ✨ ---
    characteristics = {
        "안정형": {
            "설명": "예금이나 적금 수준의 수익률을 기대하며, 투자원금에 손실이 발생하는 것을 원하지 않습니다.",
            "추천상품": "원금손실의 우려가 없는 상품에 투자하는 것이 바람직하며 **CMA와 MMF**가 좋습니다."
        },
        "안정추구형": {
            "설명": "투자원금의 손실위험은 최소화하고, 이자소득이나 배당소득 수준의 안정적인 투자를 목표로 합니다.\n\n"
                      "다만 수익을 위해 단기적인 손실을 수용할 수 있으며, 예·적금보다 높은 수익을 위해 자산 중 일부를 변동성 높은 상품에 투자할 의향이 있습니다.",
            "추천상품": "**채권형펀드**가 적당하며, 그중에서도 **장기회사채펀드** 등이 좋습니다."
        },
        "위험중립형": {
            "설명": "투자에는 그에 상응하는 투자위험이 있음을 충분히 인식하고 있으며, 예·적금보다 높은 수익을 기대할 수 있다면 일정 수준의 손실위험을 감수할 수 있습니다.",
            "추천상품": "**적립식펀드**나 **주가연동상품**처럼 중위험 펀드로 분류되는 상품을 선택하는 것이 좋습니다."
        },
        "적극투자형": {
            "설명": "투자원금의 보전보다는 위험을 감내하더라도 높은 수준의 투자수익을 추구합니다.\n\n"
                      "투자자금의 상당 부분을 주식, 주식형펀드 또는 파생상품 등의 위험자산에 투자할 의향이 있습니다.",
            "추천상품": "**국내외 주식형펀드**와 **원금비보장형 주가연계증권(ELS)** 등 고수익·고위험 상품에 투자할 수 있습니다."
        },
        "공격투자형": {
            "설명": "시장평균수익률을 훨씬 넘어서는 높은 수준의 투자수익을 추구하며, 이를 위해 자산가치의 변동에 따른 손실위험을 적극 수용할 수 있습니다.\n\n"
                      "투자자금 대부분을 주식, 주식형펀드 또는 파생상품 등의 위험자산에 투자할 의향이 있습니다.",
            "추천상품": "**주식 비중이 70% 이상인 고위험 펀드**가 적당하고, **자산의 10% 정도는 직접투자(주식)**도 고려해볼 만합니다."
        },
    }
    char = characteristics[investment_type]

    st.info(f"**{investment_type} 특징:**\n\n{char['설명']}")
    st.success(f"**추천 투자상품:**\n\n{char['추천상품']}")

    # --- ✨ 여기까지 수정 ✨ ---

    st.markdown("---")

    # 안정형과 공격투자형 모두 대시보드 접근 제한
    if investment_type == "안정형":
        st.markdown("<h3 style='color: red; text-align: center;'>⚠️ 종목 추천 대상자가 아닙니다!</h3>", unsafe_allow_html=True)
        st.info("이 앱은 투자 상품 추천을 목적으로 하며, '안정형' 투자 성향에는 적합한 추천을 제공하지 않습니다.")
        st.markdown("---")

        col1 = st.columns(1)[0]
        with col1:
            if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True, type="primary"):
                st.session_state.reset_survey_flag = True
                st.switch_page("pages/01_questionnaire.py") 
                
    elif investment_type == "공격투자형":
        st.markdown("<h3 style='color: #FF6B35; text-align: center;'>⚠️ 고위험 투자성향으로 인한 서비스 제한 안내</h3>", unsafe_allow_html=True)
        st.warning("""
        **회원님께서는 '공격투자형' 투자성향으로 분류되었습니다.**
        
        공격투자형은 매우 높은 위험 감수 성향을 나타내며, 이에 따라 저희 서비스에서 제공하는 일반적인 종목 추천이 회원님의 극단적인 위험 선호도와 맞지 않을 수 있습니다.
        
        **양해 말씀:**
        - 본 서비스는 안정추구형~적극투자형 투자자를 위한 균형잡힌 포트폴리오 추천에 특화되어 있습니다
        - 공격투자형 성향에 적합한 극고위험 상품 추천은 별도의 전문 상담이 필요합니다
        - 보다 안전하고 체계적인 투자를 위해 설문을 다시 검토해보시기를 권장드립니다
        """)
        st.markdown("---")

        col1 = st.columns(1)[0]
        with col1:
            if st.button("↩️ 설문으로 돌아가 수정하기", use_container_width=True, type="primary"):
                st.session_state.reset_survey_flag = True
                st.switch_page("pages/01_questionnaire.py") 
    else:
        # 안정추구형, 위험중립형, 적극투자형만 대시보드 접근 가능
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
