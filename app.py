# app.py

import streamlit as st
from utils import questions, validate_answers, show_footer

st.set_page_config(page_title="투자성향 진단", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

if 'answers' not in st.session_state: st.session_state.answers = {}
if 'survey_completed' not in st.session_state: st.session_state.survey_completed = False
if 'validation_errors' not in st.session_state: st.session_state.validation_errors = set()

def update_answers():
    for key in questions.keys():
        if key == "investment_experience":
            selected_indices = []
            for j in range(len(questions[key]['options'])):
                if st.session_state.get(f"checkbox_{key}_{j}", False):
                    selected_indices.append(j)
            st.session_state.answers[key] = selected_indices
        else:
            if f"radio_{key}" in st.session_state:
                st.session_state.answers[key] = st.session_state[f"radio_{key}"]

def survey_page():
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
            container.markdown("**(중복 선택 가능)**")
            for j, option in enumerate(question['options']):
                container.checkbox(f"{j+1}. {option}", key=f"checkbox_{key}_{j}", on_change=update_answers, value=(isinstance(current_answer, list) and j in current_answer))
        else:
            container.radio("옵션을 선택하세요:", options=list(range(len(question['options']))), format_func=lambda x: f"{x+1}. {question['options'][x]}", key=f"radio_{key}", on_change=update_answers, index=current_answer, label_visibility="collapsed")
        st.markdown("---")

    answered_count = 0
    total_questions = len(questions)
    for key in questions.keys():
        answer = st.session_state.answers.get(key)
        if key == "investment_experience":
            if answer: answered_count += 1
        elif answer is not None: answered_count += 1
    
    progress_value = answered_count / total_questions
    with progress_placeholder:
        st.progress(progress_value, text=f"진행률: {answered_count} / {total_questions} ({progress_value:.0%})")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 진단 결과 보기", type="primary", use_container_width=True):
            if validate_answers():
                st.session_state.survey_completed = True
                st.switch_page("pages/02_analyzing.py")
            else:
                st.error(f"⚠️ {len(st.session_state.validation_errors)}개의 문항에 답변이 필요합니다!")
                st.rerun()

if __name__ == "__main__":
    survey_page()
    show_footer()