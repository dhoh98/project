import streamlit as st
import time
import base64
from pathlib import Path

# --- 페이지 설정 ---
st.set_page_config(
    page_title="분석 중...",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS 정의 (애니메이션 포함) ---
st.markdown("""
    <style>
        /* 기본 UI 숨기기 */
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        /* 아이콘 회전 애니메이션 */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .spinning-brain {
            animation: spin 4s linear infinite; /* 4초에 한 바퀴, 무한 반복 */
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
            width: 1.5em; /* 점 세 개가 들어갈 공간 확보 */
            text-align: left;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 이미지 파일을 Base64로 인코딩하는 함수 ---
def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- 직접 접근 방지 로직 ---
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("app.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()

# --- 메인 로직 ---
def analyzing_page():
    # 이미지 로드 또는 이모지 대체
    image_path = Path(__file__).parent.parent / "assets/brain_icon.png"
    image_base64 = get_image_as_base64(image_path)
    
    if image_base64:
        image_html = f'<img src="data:image/png;base64,{image_base64}" width="100" class="spinning-brain">' # 크기 줄이고, 회전 클래스 적용
    else:
        image_html = '<span style="font-size: 80px; display: inline-block;" class="spinning-brain">🧠</span>' # 회전 클래스 적용

    st.title("🔬 답변을 바탕으로 투자 성향을 분석하고 있습니다.")
    st.markdown("---")

    # 컨테이너 크기 조정을 위해 컬럼 비율 변경
    col1, col2, col3 = st.columns([1, 2, 1]) 

    with col2:
        # 수정된 컨테이너
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

        # 동적 프로그레스 바
        progress_bar = st.progress(0, text="분석 시작... 0%")
        status_placeholder = st.empty()

    # 분석 과정 시뮬레이션
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