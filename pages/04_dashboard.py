# pages/04_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# --- 1. 연도별 CAGR 평균 계산 함수 ---
def calculate_yearly_recommended_cagr(df_full, recommended_df_latest_year):
    """
    최신 연도 (2022년) 기준 추천된 종목들의 2017-2022년 연도별 CAGR 평균을 계산하고,
    데이터가 없는 연도는 해당 추천 종목들의 전체 기간 평균 CAGR로 대체합니다.
    """
    # '회계년도' 컬럼을 정수형으로 변환 (오류 방지)
    if '회계년도' in df_full.columns:
        df_full['회계년도'] = pd.to_numeric(df_full['회계년도'], errors='coerce').astype('Int64')
        df_full.dropna(subset=['회계년도'], inplace=True) # 변환 실패한 행 제거
    else:
        st.error("⚠️ 데이터에 '회계년도' 컬럼이 없습니다. 데이터 구조를 확인해주세요.")
        return pd.DataFrame({'회계년도': [str(y) for y in range(2017, 2023)], '추천 펀드': 0.0})

    # 최신 연도 기준으로 추천된 종목들의 고유 식별자(회사명)를 가져옵니다.
    recommended_ids = recommended_df_latest_year['회사명'].unique()

    # 전체 데이터(df_full)에서 이 추천 종목들에 해당하는 과거 데이터를 필터링합니다.
    df_recommended_historical = df_full[df_full['회사명'].isin(recommended_ids)].copy()

    # 대상 연도 범위
    all_years = list(range(2017, 2023))

    # 각 연도별 추천 종목들의 CAGR 평균 계산
    if df_recommended_historical.empty or 'CAGR' not in df_recommended_historical.columns:
        # 추천 종목에 대한 과거 데이터가 없거나 CAGR 컬럼이 없는 경우
        yearly_avg_cagr = pd.Series([0.0] * len(all_years), index=all_years)
    else:
        yearly_avg_cagr = df_recommended_historical.groupby('회계년도')['CAGR'].mean().reindex(all_years)

        # 추천 종목들의 모든 연도에 걸친 전체 CAGR 평균 계산 (결측치 대체용)
        overall_avg_cagr_for_fill = df_recommended_historical['CAGR'].mean()
        if pd.isna(overall_avg_cagr_for_fill):
            overall_avg_cagr_for_fill = 0.0 # 혹은 적절한 기본값

        # 데이터가 없는 연도는 전체 평균 CAGR로 대체
        yearly_avg_cagr = yearly_avg_cagr.fillna(overall_avg_cagr_for_fill)

    # 결과를 DataFrame으로 변환하고 '회계년도'를 문자열로 변경 (그래프 x축 표시에 용이)
    df_yearly_cagr = yearly_avg_cagr.reset_index()
    df_yearly_cagr.columns = ['회계년도', '추천 펀드']
    df_yearly_cagr['회계년도'] = df_yearly_cagr['회계년도'].astype(str)

    return df_yearly_cagr

# --- 2. 꺾은선 그래프 표현 함수 ---
def create_benchmark_chart(df_recommended_yearly_cagr):
    """
    추천 펀드의 연도별 CAGR 평균과 벤치마크를 비교하는 차트를 생성합니다.
    """
    # 벤치마크 데이터
    benchmark_data = {
        'year': ['2017', '2018', '2019', '2020', '2021', '2022'],
        '국고채 3년': [1.80, 2.10, 1.53, 0.99, 1.39, 3.20],
        '국고채 5년': [2.00, 2.31, 1.59, 1.23, 1.72, 3.32],
        '국고채 10년': [2.28, 2.50, 1.70, 1.50, 2.07, 3.37],
        '회사채 3년': [2.33, 2.65, 2.02, 2.13, 2.08, 4.16],
        'CD 91일': [1.44, 1.68, 1.69, 0.92, 0.85, 2.49],
        '콜금리': [1.26, 1.52, 1.59, 0.70, 0.61, 2.02],
        '기준금리': [1.50, 1.75, 1.25, 0.50, 1.00, 3.25],
        'KOSPI': [21.78, -17.69, 9.34, 32.10, 1.13, -25.17],
        'KOSDAQ': [26.32, -16.84, 0.07, 43.68, 5.77, -34.55]
    }
    
    df_benchmark = pd.DataFrame(benchmark_data)
    
    # Plotly 차트 생성
    fig = go.Figure()
    
    # 추천 펀드 연도별 CAGR (다이아몬드 마커, 굵은 선으로 강조)
    fig.add_trace(go.Scatter(
        x=df_recommended_yearly_cagr['회계년도'],
        y=df_recommended_yearly_cagr['추천 펀드'],
        mode='lines+markers',
        name='추천 펀드 (연도별 CAGR)',
        line=dict(color='#FF6B35', width=4), # 굵은 선
        marker=dict(symbol='diamond', size=10), # 다이아몬드 마커
        hovertemplate='<b>연도:</b> %{x}<br><b>추천 펀드 CAGR:</b> %{y:.2f}%<extra></extra>' # 호버 효과
    ))
    
    # 주요 벤치마크들 (KOSPI, KOSDAQ, 국고채 3년)
    colors = {
        '국고채 3년': '#4CAF50',
        'KOSPI': '#2196F3',
        'KOSDAQ': '#9C27B0'
    }
    
    for col, color in colors.items():
        fig.add_trace(go.Scatter(
            x=df_benchmark['year'],
            y=df_benchmark[col],
            mode='lines+markers',
            name=col,
            line=dict(color=color, width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>연도:</b> %{{x}}<br><b>{col} 수익률:</b> %{{y:.2f}}%<extra></extra>' # 호버 효과
        ))
    
    # 레이아웃 설정
    fig.update_layout(
        title="📈 추천 펀드 vs 벤치마크 수익률 비교",
        xaxis_title="연도",
        yaxis_title="수익률 (%)",
        hovermode='x unified', # 마우스를 올리면 해당 연도의 모든 정보가 표시됨
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )
    
    return fig, df_benchmark

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
    
    recommended_df_latest_year = st.session_state.recommended_fund_stocks

    if not recommended_df_latest_year.empty:
        # --- 성과 요약 ---
        st.subheader("📊 추천 펀드 성과 요약")
        
        # 포트폴리오 성과 계산 (최신 연도 기준)
        average_excess_return = recommended_df_latest_year['초과수익률_apply'].mean() if '초과수익률_apply' in recommended_df_latest_year.columns else 0
        average_volatility = recommended_df_latest_year['연간변동성'].mean() if '연간변동성' in recommended_df_latest_year.columns else 0

        # 연도별 추천 펀드 CAGR 계산
        df_recommended_yearly_cagr = calculate_yearly_recommended_cagr(df_full, recommended_df_latest_year)
        overall_avg_cagr_recommended = df_recommended_yearly_cagr['추천 펀드'].mean() # 6년간 평균 CAGR

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="평균 초과수익률 (vs 국고채)", value=f"{average_excess_return:.2f} %p")
        with col2:
            st.metric(label="평균 연간복리수익률 (6년간 CAGR)", value=f"{overall_avg_cagr_recommended:.2f} %")
        with col3:
            st.metric(label="평균 연간변동성", value=f"{average_volatility:.2f} %")
        
        st.info(f"💡 이 펀드는 회원님의 '{investment_type}' 성향에 맞춰, {df_full['회계년도'].max()}년 데이터 기준 '연간변동성'이 {investment_type} 기준에 부합하며 'CAGR'이 높은 상위 10개 종목으로 구성되었습니다.")
        
        # --- 벤치마크 비교 차트 추가 ---
        st.markdown("---")
        st.subheader("📈 벤치마크 대비 성과 비교")
        
        fig, benchmark_df = create_benchmark_chart(df_recommended_yearly_cagr)
        st.plotly_chart(fig, use_container_width=True)
        
        # 벤치마크 평균 수익률 계산 및 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            kospi_avg = benchmark_df['KOSPI'].mean()
            st.metric(
                label="KOSPI 6년간 평균",
                value=f"{kospi_avg:.2f}%",
                delta=f"{overall_avg_cagr_recommended - kospi_avg:.2f}%p"
            )
        with col2:
            kosdaq_avg = benchmark_df['KOSDAQ'].mean()
            st.metric(
                label="KOSDAQ 6년간 평균",
                value=f"{kosdaq_avg:.2f}%",
                delta=f"{overall_avg_cagr_recommended - kosdaq_avg:.2f}%p"
            )
        with col3:
            bond3y_avg = benchmark_df['국고채 3년'].mean()
            st.metric(
                label="국고채 3년 6년간 평균",
                value=f"{bond3y_avg:.2f}%",
                delta=f"{overall_avg_cagr_recommended - bond3y_avg:.2f}%p"
            )
        with col4:
            st.metric(
                label="추천 펀드 6년간 CAGR",
                value=f"{overall_avg_cagr_recommended:.2f}%",
                delta="기준"
            )
        
        st.markdown("---") 

        # --- 3. 상세 정보 테이블 추가 ---
        st.subheader("📊 연도별 및 평균 성과 상세 정보")

        # 테이블을 위한 데이터 결합
        df_combined_table = df_recommended_yearly_cagr.set_index('회계년도')
        df_combined_table.index.name = '연도'

        # 벤치마크 데이터 중 필요한 컬럼만 선택 후 인덱스 설정
        benchmark_table_cols = ['year', 'KOSPI', 'KOSDAQ', '국고채 3년']
        df_benchmark_for_table = benchmark_df[benchmark_table_cols].set_index('year')
        df_benchmark_for_table.index.name = '연도'

        # 두 데이터프레임을 연도 기준으로 병합 (내부 조인하여 공통 연도만 유지)
        df_final_detail_table = pd.concat([df_combined_table, df_benchmark_for_table], axis=1, join='inner')

        # '6년간 평균' 행 추가
        avg_row_data = df_final_detail_table.mean(numeric_only=True).to_frame().T
        avg_row_data.index = ['6년간 평균']
        df_final_detail_table = pd.concat([df_final_detail_table, avg_row_data])

        # '추천 펀드와의 차이' 행 추가
        delta_row = pd.DataFrame(index=['추천 펀드와의 차이'], columns=df_final_detail_table.columns)
        delta_row['추천 펀드'] = '' # 추천 펀드 자체는 차이 없음
        
        # 6년간 평균 값 참조하여 델타 계산
        fund_avg = df_final_detail_table.loc['6년간 평균', '추천 펀드']
        for col in ['KOSPI', 'KOSDAQ', '국고채 3년']:
            benchmark_avg = df_final_detail_table.loc['6년간 평균', col]
            delta_row[col] = fund_avg - benchmark_avg

        df_final_detail_table = pd.concat([df_final_detail_table, delta_row])

        # 데이터 포맷팅 (소수점 두 자리 및 '%' 추가)
        # 문자열이 아닌 숫자형 컬럼에만 적용
        for col in df_final_detail_table.columns:
            # '추천 펀드와의 차이' 행의 '추천 펀드' 컬럼은 문자열이므로 제외
            if col == '추천 펀드' and '추천 펀드와의 차이' in df_final_detail_table.index:
                continue
            
            # 숫자형 데이터에만 포맷팅 적용
            df_final_detail_table[col] = df_final_detail_table[col].apply(
                lambda x: f"{x:.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else x
            )

        st.dataframe(df_final_detail_table, use_container_width=True)

        st.markdown("---") 

        st.subheader(f"✨ 추천 펀드 구성 종목 ({len(recommended_df_latest_year)}개)")
        
        # 추천 종목 목록을 테이블로 표시 (최신 연도 기준)
        cols_to_display_rec = ['회사명', '거래소코드', 'CAGR', '연간변동성', '초과수익률_apply', 'target_class']
        display_recommended_df = recommended_df_latest_year[[col for col in cols_to_display_rec if col in recommended_df_latest_year.columns]].copy()
        display_recommended_df.columns = ['회사명', '거래소코드', 'CAGR (%)', '연간변동성 (%)', '초과수익률 (%)', '투자성향분류']
        
        st.dataframe(display_recommended_df, hide_index=True, use_container_width=True)

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
            if not recommended_df_latest_year.empty:
                st.session_state['포트폴리오 선택'] = recommended_df_latest_year['회사명'].tolist()
            else:
                st.session_state['포트폴리오 선택'] = []
            st.switch_page("pages/05_individual_stock_analysis.py")
    
    st.markdown("</div>", unsafe_allow_html=True)