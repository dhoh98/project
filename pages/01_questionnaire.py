import streamlit as st
from utils import questions, calculate_score, validate_answers, show_footer, reset_survey_state

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="투자성향 진단 설문",
    page_icon="🏠",
    layout="wide"
)

# --- 로그인 확인 및 설문 상태 초기화 ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if st.session_state.get('reset_survey_flag', False):
    reset_survey_state()

# --- 설문 페이지의 CSS ---
st.markdown("""
<style>
    /* 설문 옵션(라디오/체크박스) 글자 크게 */
    div[data-testid="stRadio"] label span,
    div[data-testid="stCheckbox"] label span {
        font-size: 1.25em !important;
        line-height: 1.7;
    }
    /* 문항 제목 */
    h3 {
        font-size: 1.5em;
        margin-bottom: 0.8em;
    }
    /* 에러/경고 메시지 크게 */
    div[data-testid="stAlert"] {
        font-size: 1.2em;
        font-weight: bold;
        color: #d32f2f !important;
    }
    /* 배경 및 레이아웃 기본값 */
    [data-testid="stAppViewContainer"] > .main { background: none; }
    .main .block-container {
        display: block;
        align-items: initial;
        justify-content: initial;
        min-height: auto;
        padding-top: 2rem !important;
    }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

def questionnaire_page():
    with st.sidebar:
        st.success(f"**{st.session_state.username}**님, 환영합니다!")
        if st.button("↩️ 로그아웃"):
            st.session_state.clear()
            st.session_state.logged_in = False
            st.switch_page("app.py")

    if 'answers' not in st.session_state: st.session_state.answers = {}
    if 'survey_completed' not in st.session_state: st.session_state.survey_completed = False
    if 'validation_errors' not in st.session_state: st.session_state.validation_errors = set()

    def update_answers():
        for key in questions.keys():
            if key == "investment_experience":
                selected_indices = [j for j, _ in enumerate(questions[key]['options']) if st.session_state.get(f"checkbox_{key}_{j}", False)]
                st.session_state.answers[key] = selected_indices
            elif f"radio_{key}" in st.session_state:
                st.session_state.answers[key] = st.session_state[f"radio_{key}"]

    st.title("📊 투자성향 진단 설문")
    progress_placeholder = st.container()
    st.markdown("---")

    for key, question in questions.items():
        is_error = key in st.session_state.validation_errors
        current_answer = st.session_state.answers.get(key)
        container = st.container()

        if is_error:
            container.markdown(f"<h3 style='color: #ff4444;'>**{question['title']}** ⚠️ 필수 문항</h3>", unsafe_allow_html=True)
        else:
            container.subheader(f"**{question['title']}**")

        if key == "investment_experience":
            for j, option in enumerate(question['options']):
                is_checked = isinstance(current_answer, list) and j in current_answer
                container.checkbox(f"{j+1}. {option}", key=f"checkbox_{key}_{j}", on_change=update_answers, value=is_checked)
        else:
            index_to_pass = current_answer if current_answer is not None else None
            container.radio("옵션을 선택하세요:",
                            options=list(range(len(question['options']))),
                            format_func=lambda x: f"{x+1}. {question['options'][x]}",
                            key=f"radio_{key}",
                            on_change=update_answers,
                            index=index_to_pass,
                            label_visibility="collapsed")
        st.markdown("---")

    answered_count = sum(1 for key in questions if key in st.session_state.answers and st.session_state.answers[key] is not None and (st.session_state.answers[key] != [] if key == "investment_experience" else True))
    progress_value = answered_count / len(questions) if questions else 0
    with progress_placeholder:
        st.progress(progress_value)
        st.markdown(
            f"<div style='font-size:1.3em; font-weight:bold; margin-top:0.5em;'>"
            f"진행률: {answered_count} / {len(questions)} ({progress_value:.0%})</div>",
            unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 진단 결과 보기", type="primary", use_container_width=True):
            if validate_answers():
                st.session_state.survey_completed = True
                st.switch_page("pages/02_analyzing.py")
            else:
                st.error(f"⚠️ {len(st.session_state.validation_errors)}개의 문항에 답변이 필요합니다!")
                st.rerun()

    show_footer()

if __name__ == '__main__':
    questionnaire_page()
