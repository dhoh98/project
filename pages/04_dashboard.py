# pages/04_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import time
from utils import load_and_process_data, reset_survey_state, get_recommended_stocks

# 페이지 설정
st.set_page_config(page_title="추천 펀드", page_icon="💰", layout="wide")

# --- 모든 페이지 공통 UI 숨김 CSS ---
st.markdown("""
    <style>
        /* 모든 페이지 공통: 헤더, 사이드바 내비게이션, 사이드바 컨트롤 버튼, 푸터 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: block; }
        
        /* 테이블 정렬 아이콘 숨기기 */
        [data-testid="stColumnSortIcon"] { display: none; } 

        /* 선물 상자 애니메이션 */
        @keyframes wobble {
            0% { transform: translateX(0) rotate(0deg); }
            10% { transform: translateX(-10px) rotate(-8deg); }
            20% { transform: translateX(10px) rotate(8deg); }
            30% { transform: translateX(-8px) rotate(-5deg); }
            40% { transform: translateX(8px) rotate(5deg); }
            50% { transform: translateX(-5px) rotate(-3deg); }
            60% { transform: translateX(5px) rotate(3deg); }
            70% { transform: translateX(-3px) rotate(-1deg); }
            80% { transform: translateX(3px) rotate(1deg); }
            90% { transform: translateX(-1px) rotate(0deg); }
            100% { transform: translateX(0) rotate(0deg); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        /* 선물상자 열리는 애니메이션 */
        @keyframes giftOpen {
            0% { 
                transform: scale(1) rotate(0deg);
                opacity: 1;
            }
            25% { 
                transform: scale(1.2) rotate(-10deg);
                opacity: 0.8;
            }
            50% { 
                transform: scale(1.5) rotate(10deg);
                opacity: 0.6;
            }
            75% { 
                transform: scale(2) rotate(-5deg);
                opacity: 0.3;
            }
            100% { 
                transform: scale(2.5) rotate(0deg);
                opacity: 0;
            }
        }
        
        /* 반짝이는 효과 */
        @keyframes sparkle {
            0%, 100% { opacity: 0; transform: scale(0) rotate(0deg); }
            50% { opacity: 1; transform: scale(1) rotate(180deg); }
        }
        
        .wobbling-gift-box {
            animation: wobble 1.2s ease-in-out, pulse 2s ease-in-out infinite;
            transform-origin: center;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .opening-gift-box {
            animation: giftOpen 2s ease-in-out forwards;
            transform-origin: center;
            display: inline-block;
        }
        
        .sparkles {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 30px;
            pointer-events: none;
        }
        
        .sparkle {
            position: absolute;
            animation: sparkle 1.5s ease-in-out infinite;
        }
        
        .sparkle:nth-child(1) { top: -40px; left: -40px; animation-delay: 0s; }
        .sparkle:nth-child(2) { top: -40px; right: -40px; animation-delay: 0.3s; }
        .sparkle:nth-child(3) { bottom: -40px; left: -40px; animation-delay: 0.6s; }
        .sparkle:nth-child(4) { bottom: -40px; right: -40px; animation-delay: 0.9s; }
        .sparkle:nth-child(5) { top: -20px; left: 0; animation-delay: 1.2s; }
        
        .gift-container {
            text-align: center;
            padding: 20px;
            margin: 20px 0;
            position: relative;
            min-height: 200px;
        }
        
        /* 페이드인 애니메이션 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.8s ease-out;
        }
        
        /* 선물 내용물 등장 애니메이션 */
        @keyframes slideUp {
            from { 
                opacity: 0; 
                transform: translateY(50px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        .slide-up {
            animation: slideUp 1s ease-out;
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

# --- 페이지 시작 ---
st.title("💰 투자성향 맞춤 추천 펀드")

investment_type = st.session_state.get('investment_type', '위험중립형')

st.markdown(f"### 🎉 회원님의 투자성향은 **<span style='color: #4CAF50;'>{investment_type}</span>** 입니다!", unsafe_allow_html=True)
st.write(f"아래는 **{investment_type}** 투자 성향에 맞춰 엄선된 펀드형 추천 포트폴리오입니다.")
st.markdown("---")

# 데이터 로드
df_full = load_and_process_data()

if df_full.empty:
    st.warning("데이터 로드에 실패했거나 처리할 종목이 없습니다.")
    st.stop()

# --- 상태 초기화 ---
if 'animation_stage' not in st.session_state:
    st.session_state.animation_stage = 'initial'  # initial -> animating -> completed

# 단계별 처리
if st.session_state.animation_stage == 'initial':
    # 초기 상태: 선물 상자 표시
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ 지금 바로 회원님께 맞는 추천 펀드를 확인하세요! ✨</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>아래 선물 상자를 클릭해 주세요.</p>", unsafe_allow_html=True)
    
    # 선물 상자 컨테이너
    st.markdown("""
        <div class='gift-container'>
            <div style='font-size: 120px;'>🎁</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎁 추천 펀드 공개하기", type="primary", use_container_width=True):
            st.session_state.animation_stage = 'animating'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.animation_stage == 'animating':
    # 애니메이션 상태: 선물 상자가 열리는 효과만 표시 (제목/설명은 그대로)
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ 지금 바로 회원님께 맞는 추천 펀드를 확인하세요! ✨</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>선물 상자를 열고 있어요...</p>", unsafe_allow_html=True)
    
    # 선물 상자 열리는 애니메이션과 반짝이만 표시
    st.markdown("""
        <div class='gift-container'>
            <div class='opening-gift-box' style='font-size: 120px;'>🎁</div>
            <div class='sparkles'>
                <div class='sparkle'>✨</div>
                <div class='sparkle'>⭐</div>
                <div class='sparkle'>💫</div>
                <div class='sparkle'>🌟</div>
                <div class='sparkle'>✨</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 펀드 데이터 로드 (애니메이션 중에 미리 준비)
    if 'recommended_fund_stocks' not in st.session_state:
        st.session_state.recommended_fund_stocks = get_recommended_stocks(df_full, investment_type)
    
    # 애니메이션 시간 대기
    time.sleep(2.5)  # 선물상자 열리는 애니메이션 시간
    
    # 풍선 애니메이션
    st.balloons()
    
    # 다음 단계로 이동
    st.session_state.animation_stage = 'completed'
    st.rerun()

else:  # animation_stage == 'completed'
    # 완료 상태: 펀드 정보 표시
    st.markdown("<div class='slide-up'>", unsafe_allow_html=True)
    
    recommended_df = st.session_state.recommended_fund_stocks

    if not recommended_df.empty:
        st.subheader(f"✨ 추천 펀드 구성 종목 ({len(recommended_df)}개)")
        
        # 추천 종목 목록을 테이블로 표시
        cols_to_display_rec = ['회사명', '거래소코드', 'CAGR', '연간변동성', '초과수익률_apply', 'target_class']
        display_recommended_df = recommended_df[[col for col in cols_to_display_rec if col in recommended_df.columns]].copy()
        display_recommended_df.columns = ['회사명', '거래소코드', 'CAGR (%)', '연간변동성 (%)', '초과수익률 (%)', '투자성향분류']
        
        st.dataframe(display_recommended_df, hide_index=True, use_container_width=True)
        st.markdown("---")

        # 추천 펀드의 총 성과 요약
        st.subheader("📊 추천 펀드 성과 요약")
        
        benchmark_rate = 2.8

        # 포트폴리오 성과 계산
        average_excess_return = recommended_df['초과수익률_apply'].mean() if '초과수익률_apply' in recommended_df.columns else 0
        average_cagr = recommended_df['CAGR'].mean() if 'CAGR' in recommended_df.columns else 0
        average_volatility = recommended_df['연간변동성'].mean() if '연간변동성' in recommended_df.columns else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="평균 초과수익률 (vs 국고채)", value=f"{average_excess_return:.2f} %p")
        with col2:
            st.metric(label="평균 연간복리수익률 (CAGR)", value=f"{average_cagr:.2f} %")
        with col3:
            st.metric(label="평균 연간변동성", value=f"{average_volatility:.2f} %")
        
        st.info(f"💡 이 펀드는 회원님의 '{investment_type}' 성향에 맞춰, {df_full['회계년도'].max()}년 데이터 기준 '연간변동성'이 {investment_type} 기준에 부합하며 'CAGR'이 높은 상위 10개 종목으로 구성되었습니다.")

    else:
        st.warning("회원님의 투자성향에 맞는 추천 종목을 찾지 못했습니다. 개별 종목 분석 페이지에서 직접 종목을 찾아보세요.")
    
    st.markdown("---")
    st.subheader("📋 다음 단계")

    # 다음 페이지로 이동 버튼
    col_survey_btn, col_stock_btn = st.columns(2) 
    with col_survey_btn:
        if st.button("🏠 설문 페이지로 돌아가기", use_container_width=True):
            # 애니메이션 상태도 초기화
            st.session_state.animation_stage = 'initial'
            if 'recommended_fund_stocks' in st.session_state:
                del st.session_state.recommended_fund_stocks
            reset_survey_state()
            st.switch_page("pages/01_questionnaire.py")
    
    with col_stock_btn:
        if st.button("📈 개별 종목 분석 및 포트폴리오 구성하기", type="primary", use_container_width=True):
            if not recommended_df.empty:
                st.session_state['포트폴리오 선택'] = recommended_df['회사명'].tolist()
            else:
                st.session_state['포트폴리오 선택'] = []
            st.switch_page("pages/05_individual_stock_analysis.py")
    
    st.markdown("</div>", unsafe_allow_html=True)