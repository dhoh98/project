import streamlit as st
from utils import questions, validate_answers, show_footer
import sqlite3
import hashlib

# --- 데이터베이스 설정 ---
def setup_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="로그인 페이지",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 로그인 UI 스타일 (탭 기능 추가) ---
def auth_css():
    st.markdown("""
    <style>
        /* Streamlit 기본 UI 숨기기 */
        [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none; }
        
        /* 앱 배경 그라데이션 */
        [data-testid="stAppViewContainer"] > .main {
            background-image: linear-gradient(to top right, #0a192f, #1e3a5f, #4a6da7);
            background-size: cover;
        }

        /* st.columns를 포함하는 메인 블록을 Flexbox로 만들어 수직 중앙 정렬 */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 0 !important;
        }

        /* 로그인 폼 컨테이너 (st.columns의 중앙 컬럼을 타겟팅) */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            width: 100%;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        h1 { font-size: 2.2em; color: #ffffff; font-weight: 600; margin-bottom: 25px; letter-spacing: 2px; }
        
        /* 로그인/회원가입 선택 라디오 버튼 스타일 */
        div[data-testid="stRadio"] {
            display: flex; justify-content: center; margin-bottom: 25px;
        }
        div[data-testid="stRadio"] label {
            padding: 8px 20px; border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px; margin: 0 5px; transition: all 0.3s;
            background-color: transparent; color: rgba(255,255,255,0.7);
        }
        div[data-testid="stRadio"] input:checked + div {
            background-color: rgba(0, 198, 255, 0.3);
            color: white; border-color: #00c6ff;
        }

        div[data-testid="stTextInput"] input {
            background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px; color: #000000 !important; padding: 12px; transition: all 0.3s;
        }
        
        div[data-testid="stButton"] > button {
            width: 100%; padding: 12px 0; background: linear-gradient(45deg, #00c6ff, #0072ff);
            border: none; border-radius: 10px; color: white; font-weight: bold; transition: all 0.3s;
        }
    </style>
    """, unsafe_allow_html=True)


# --- 로그인/회원가입 페이지 함수 ---
def auth_page():
    setup_database()
    auth_css()

    left_space, form_col, right_space = st.columns((1.5, 0.8, 1.5))

    with form_col:
        choice = st.radio("choice", ["로그인", "회원가입"], horizontal=True, label_visibility="collapsed")
        
        if choice == "로그인":
            st.markdown("<h1>📊 부실하체트레이너</h1>", unsafe_allow_html=True)
            username = st.text_input("아이디", key="login_user", placeholder="아이디")
            password = st.text_input("비밀번호", type="password", key="login_pass", placeholder="비밀번호")
            
            if st.button("로그인", key="login_btn"):
                # 데모 로그인 + DB 로그인 동시 처리
                if username == "beta" and password == "1234":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    conn = sqlite3.connect('user_data.db')
                    c = conn.cursor()
                    c.execute('SELECT password FROM users WHERE username = ?', (username,))
                    db_password_hash = c.fetchone()
                    conn.close()

                    if db_password_hash and db_password_hash[0] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 잘못되었습니다.")

        elif choice == "회원가입":
            st.markdown("<h1>📝 회원가입</h1>", unsafe_allow_html=True)
            new_username = st.text_input("사용할 아이디", key="signup_user", placeholder="아이디")
            new_password = st.text_input("사용할 비밀번호", type="password", key="signup_pass", placeholder="비밀번호")
            confirm_password = st.text_input("비밀번호 확인", type="password", key="signup_confirm", placeholder="비밀번호 확인")

            if st.button("가입하기", key="signup_btn"):
                if new_password == confirm_password:
                    if len(new_password) >= 4:
                        try:
                            conn = sqlite3.connect('user_data.db')
                            c = conn.cursor()
                            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, hash_password(new_password)))
                            conn.commit()
                            st.success("회원가입 성공! 이제 로그인해주세요.")
                        except sqlite3.IntegrityError:
                            st.error("이미 존재하는 아이디입니다.")
                        finally:
                            conn.close()
                    else:
                        st.warning("비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.error("비밀번호가 일치하지 않습니다.")

# --- 설문 페이지 함수 (이전과 동일) ---
def survey_page():
    # ... (코드가 길어 생략, 이전과 동일하게 유지) ...
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] > .main { background: none; }
        .main .block-container { 
            display: block;
            align-items: initial;
            justify-content: initial;
            min-height: auto;
            padding-top: 2rem !important;
        }
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: block; }
    </style>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.success(f"**{st.session_state.username}**님, 환영합니다!")
        if st.button("↩️ 로그아웃"):
            keys_to_delete = [k for k in st.session_state.keys() if k != 'logged_in']
            for key in keys_to_delete:
                del st.session_state[key]
            st.session_state.logged_in = False
            st.rerun()
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
            container.markdown("**(중복 선택 가능)**")
            for j, option in enumerate(question['options']):
                is_checked = isinstance(current_answer, list) and j in current_answer
                container.checkbox(f"{j+1}. {option}", key=f"checkbox_{key}_{j}", on_change=update_answers, value=is_checked)
        else:
            container.radio("옵션을 선택하세요:", options=list(range(len(question['options']))), format_func=lambda x: f"{x+1}. {question['options'][x]}", key=f"radio_{key}", on_change=update_answers, index=current_answer, label_visibility="collapsed")
        st.markdown("---")
    answered_count = sum(1 for key in questions if st.session_state.answers.get(key))
    progress_value = answered_count / len(questions) if questions else 0
    with progress_placeholder:
        st.progress(progress_value, text=f"진행률: {answered_count} / {len(questions)} ({progress_value:.0%})")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 진단 결과 보기", type="primary", use_container_width=True):
            if validate_answers():
                st.session_state.survey_completed = True
                st.switch_page("pages/03_result.py")
            else:
                st.error(f"⚠️ {len(st.session_state.validation_errors)}개의 문항에 답변이 필요합니다!")
                st.rerun()
    show_footer()


# --- 메인 라우터 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    survey_page()
else:
    auth_page()