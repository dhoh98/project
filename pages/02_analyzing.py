# pages/02_analyzing.py

import streamlit as st
import time
import base64
from pathlib import Path
# from utils import check_session_timeout # check_session_timeout 제거로 불필요

# --- 페이지 설정 ---
st.set_page_config(
    page_title="분석 중...",
    page_icon="🔬",
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
        footer { display: none; } 

        /* 중앙 정렬을 위한 메인 컨테이너 (이 페이지에 특화된 스타일) */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 0 !important;
        }
        
        /* 아이콘 회전 애니메이션 */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .spinning-brain {
            animation: spin 4s linear infinite;
        }

        /* 텍스트 점(.) 애니메이션 */
        @keyframes ellipsis {
            0% { content: "."; }
            33% { content: ".."; }
            66% { content: "..."; }
            100% { content: "."; }
        }
        .analyzing-text::after {
            content: ".";
            animation: ellipsis 1.5s infinite;
            display: inline-block;
            width: 1.5em;
            text-align: left;
        }

        /* `st.error`나 `st.warning` 등 메시지 컨테이너의 텍스트 색상 조정 (선택 사항) */
        div[data-testid="stAlert"] {
            color: initial; 
        }
    </style>
    """, unsafe_allow_html=True)

# --- 직접 접근 방지 로직 (로그인 여부 및 설문 완료 여부 확인) ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()


# --- 이미지 파일을 Base64로 인코딩하는 함수 ---
def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- 메인 로직 ---
def analyzing_page():
    image_path = Path(__file__).parent.parent / "assets/brain_icon.png"
    image_base64 = get_image_as_base64(image_path)
    
    if image_base64:
        image_html = f'<img src="data:image/png;base64,{image_base64}" width="100" class="spinning-brain">'
    else:
        image_html = '<span style="font-size: 80px; display: inline-block;" class="spinning-brain">🧠</span>'

    st.title("🔬 답변을 바탕으로 투자 성향을 분석하고 있습니다.")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1]) 

    with col2:
        st.markdown(f"""
        <div style="
            text-align: center; 
            padding: 30px 20px; 
            border-radius: 20px; 
            background-color: #e7f5ff;
            border: 2px solid #b0e0e6;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        ">
            {image_html}
            <h2 style="color: #005A9C; margin-top: 20px; margin-bottom: 25px;">
                <span class="analyzing-text">투자 성향 정밀 분석 중</span>
            </h2>
            <p style="color: #333; font-size: 1.05em;">
                제출하신 답변을 기반으로<br>
                회원님에게 꼭 맞는 투자 유형을 찾고 있습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        progress_bar = st.progress(0, text="분석 시작... 0%")
        status_placeholder = st.empty()

    analysis_steps = [
        ("연령대 및 투자 기간 분석", 15),
        ("투자 경험 및 지식 수준 평가", 40),
        ("금융 자산 및 소득 구조 확인", 65),
        ("위험 감수 성향 측정", 90),
        ("최종 투자 유형 분류", 100),
    ]

    for step_text, percentage in analysis_steps:
        time.sleep(1)
        status_placeholder.info(f"⚙️ **진행 단계:** {step_text}...")
        progress_bar.progress(percentage, text=f"분석 진행률... {percentage}%")

    time.sleep(0.5)
    status_placeholder.success("✅ 분석이 완료되었습니다! 잠시 후 결과 페이지로 이동합니다.")
    progress_bar.progress(100, text="분석 완료! 100%")
    time.sleep(1.5)

    st.switch_page("pages/03_result.py")


if __name__ == "__main__":
    analyzing_page()