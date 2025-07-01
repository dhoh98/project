# app.py (로그인 전용)

import streamlit as st
import sqlite3
import hashlib
# from datetime import datetime # check_session_timeout 제거로 datetime 불필요

# utils에서 check_session_timeout을 제거했으므로 더 이상 임포트하지 않습니다.
# 설문 관련 함수들은 app.py에서 직접 사용되지 않으므로, 이 줄은 `from utils import`만 남겨두거나 필요에 따라 다른 임포트를 추가할 수 있습니다.
# 현재 로직에서는 utils에서 직접 가져올 함수가 없습니다.
# 다만, utils.py의 questions를 참조하는 로직이 과거에 있었으므로 주석 처리하여 남겨두겠습니다.
# from utils import questions, validate_answers, show_footer 

# --- 데이터베이스 설정 ---
def setup_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def hash_password(password):
    """비밀번호를 SHA256 해시로 변환합니다."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="투자성향 진단 앱 - 로그인",
    page_icon="📊",
    layout="wide", # 로그인 페이지는 넓은 레이아웃 사용
    initial_sidebar_state="collapsed"
)

# --- 로그인 UI 스타일 (기존과 동일) ---
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
            background-color: rgba(255, 255, 255, 0.1); 
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px; 
            color: #000000 !important; /* 검정색으로 유지 */
            padding: 12px; 
            transition: all 0.3s;
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

    left_space, form_col, right_space = st.columns((1.2, 1.2, 1.2))

    with form_col:
        choice = st.radio("choice", ["로그인", "회원가입"], horizontal=True, label_visibility="collapsed")
        
        if 'choice_radio' in st.session_state and st.session_state.choice_radio == "로그인":
            choice = "로그인"
            del st.session_state.choice_radio

        if choice == "로그인":
            st.markdown("<h2>📊 로그인</h2>", unsafe_allow_html=True)
            username = st.text_input("아이디", key="login_user", placeholder="아이디")
            password = st.text_input("비밀번호", type="password", key="login_pass", placeholder="비밀번호")
            
            if st.button("로그인", key="login_btn"):
                is_authenticated = False
                if username == "beta" and password == "1234":
                    is_authenticated = True
                else:
                    conn = sqlite3.connect('user_data.db')
                    c = conn.cursor()
                    c.execute('SELECT password FROM users WHERE username = ?', (username,))
                    db_password_hash = c.fetchone()
                    conn.close()

                    if db_password_hash and db_password_hash[0] == hash_password(password):
                        is_authenticated = True
                
                if is_authenticated:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    # last_activity_timestamp 업데이트 로직 제거 (세션 타임아웃 기능 삭제로 불필요)
                    st.session_state.reset_survey_flag = True # 설문 페이지로 갈 때 초기화하도록 플래그 설정
                    st.switch_page("pages/01_questionnaire.py") # 설문 페이지로 이동
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")

        elif choice == "회원가입":
            st.markdown("<h2>📝 회원가입</h2>", unsafe_allow_html=True)
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
                            st.session_state.choice_radio = "로그인" 
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("이미 존재하는 아이디입니다.")
                        finally:
                            conn.close()
                    else:
                        st.warning("비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.error("비밀번호가 일치하지 않습니다.")

# --- 메인 라우터 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page("pages/01_questionnaire.py")
else:
    auth_page()