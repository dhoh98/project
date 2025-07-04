import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(
    page_title="중요: 투자 전 확인사항",
    page_icon="⚠️",
    layout="centered", # 이 페이지 자체는 중앙 정렬됩니다.
    initial_sidebar_state="collapsed"
)

# --- 전체 UI 숨김 및 모달 스타일 CSS ---
st.markdown("""
    <style>
        /* Streamlit 기본 UI 숨김 */
        [data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        footer {
            display: none;
        }

        /* 1. 페이지 전체 (html, body)의 배경을 어둡고 희미하게 처리 */
        html, body {
            background-color: rgba(0, 0, 0, 0.85); 
            overflow: hidden; 
            height: 100%; 
        }
        
        /* 2. Streamlit의 메인 컨테이너 (.main)는 투명하게 하고, 콘텐츠를 중앙 정렬 */
        .main {
            background-color: transparent; 
            height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 0; 
        }

        /* 3. Streamlit의 내부 블록 컨테이너 (.block-container)에 직접 모달 스타일 적용 */
        .block-container {
            max-width: 950px; /* 박스의 최대 너비를 더 크게 증가 (핵심 변경) */
            padding: 50px 70px; /* 좌우 패딩도 약간 더 늘림 */
            background-color: #fff; 
            border-radius: 20px; 
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5); 
            text-align: center;
            color: #333;
            border: none !important; 
            box-sizing: border-box; 
            flex-grow: 0; 
            
            transform: translateY(20px); 
        }

        /* block-container 내부 요소들의 스타일 조정 (글자 크기 증가) */
        h2 {
            color: #dc3545;
            font-size: 2.2em; /* h2 폰트 크기 유지 또는 미세 조정 (너무 크면 두 줄 됨) */
            font-weight: bold;
            margin-bottom: 40px; 
            white-space: nowrap; /* 텍스트를 강제로 한 줄에 표시 (overflow 시 ... 처리) */
            overflow: hidden;     /* 넘치는 텍스트 숨김 */
            text-overflow: ellipsis; /* 숨겨진 텍스트를 ...으로 표시 */
        }

        p {
            font-size: 1.3em; 
            line-height: 1.8;
            margin-bottom: 30px; 
        }

        ul {
            text-align: left;
            padding-left: 30px; 
            color: #555;
            font-size: 1.2em; 
            margin-bottom: 40px; 
            list-style-type: disc;
        }

        li {
            margin-bottom: 18px; 
        }

        strong {
            color: #222;
        }

        /* 버튼 스타일 */
        .stButton > button {
            width: 100%;
            font-size: 1.3em; 
            padding: 18px 30px; 
            border-radius: 12px; 
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 3px 8px rgba(0,0,0,0.15); 
        }

        .stButton > button:hover {
            transform: translateY(-4px); 
            box-shadow: 0 8px 20px rgba(0,0,0,0.25); 
        }
    </style>
""", unsafe_allow_html=True)

# --- 접근 제어 ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'investment_type' not in st.session_state or st.session_state.investment_type == "안정형":
    st.warning("⚠️ 잘못된 접근입니다. 투자성향 진단을 먼저 완료하거나, 해당 기능은 '안정형' 투자자에게 제공되지 않습니다.")
    st.page_link("pages/03_result.py", label="진단 결과 페이지로 돌아가기", icon="🏠")
    st.stop()

# --- 콘텐츠 (block-container 내부에 직접 렌더링) ---

# h2 태그에 해당하는 부분 (글자 크기 증가)
st.markdown("""
    <h2>⚠️ 중요: 투자 전 확인사항 (KYC Rule) ⚠️</h2>
""", unsafe_allow_html=True)

# p, ul, li, strong 태그에 해당하는 부분 (글자 크기 증가)
st.markdown("""
    <p><strong>본 앱에서 제공하는 모든 종목 추천 및 분석 정보는 투자 판단의 참고 자료이며, 투자 권유를 목적으로 하지 않습니다.</strong></p>
    <ul>
        <li><strong>투자 결정의 책임:</strong> 투자 상품은 원금 손실 위험을 포함하며, 모든 투자 결정의 최종 책임은 투자자 본인에게 있습니다.</li>
        <li><strong>개인의 판단:</strong> 제시된 정보는 사용자의 투자 성향 진단 결과를 바탕으로 한 것이지만, 개인의 재정 상황, 투자 목표, 위험 감수 능력 등을 종합적으로 고려하여 신중하게 판단하시기 바랍니다.</li>
        <li><strong>시장 변동성:</strong> 시장 상황은 언제든지 변동할 수 있으며, 과거의 수익률이 미래의 수익률을 보장하지 않습니다.</li>
    </ul>
    <p style="font-weight: bold; font-size: 1.1em; color: #333;">
        위 내용을 충분히 이해하고 투자에 따르는 위험을 인지하셨습니까?
    </p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2) # 버튼들을 가로로 나열하기 위해 Streamlit 컬럼 사용
with col1:
    if st.button("✅ 예, 이해하고 동의합니다", type="primary", use_container_width=True, key="kyc_agree"):
        st.session_state.kyc_acknowledged_for_session = True
        st.switch_page("pages/04_dashboard.py")

with col2:
    if st.button("❌ 아니오, 다시 생각해볼게요", use_container_width=True, key="kyc_disagree"):
        st.session_state.kyc_acknowledged_for_session = False
        st.switch_page("pages/03_result.py")