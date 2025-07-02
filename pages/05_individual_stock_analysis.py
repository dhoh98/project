# pages/05_individual_stock_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_and_process_data, reset_survey_state

# 페이지 설정
st.set_page_config(page_title="종목 대시보드", page_icon="📈", layout="wide")

# --- 모든 페이지 공통 UI 숨김 CSS ---
st.markdown("""
    <style>
        /* 모든 페이지 공통: 헤더, 사이드바 내비게이션, 사이드바 컨트롤 버튼, 푸터 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: block; } /* 푸터는 이 페이지에서 다시 보이게 합니다. */
        
        /* 테이블 정렬 아이콘 숨기기 (기존에 있었음) */
        [data-testid="stColumnSortIcon"] { display: none; } 

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

st.title("📈 개별 종목 분석 및 맞춤형 포트폴리오 구성")
st.markdown("자유롭게 종목을 필터링하고 선택하여 나만의 포트폴리오를 구성해 보세요.")

# 세션 상태 변수 초기화 (이 페이지에서 필요한 것들)
if 'show_results' not in st.session_state: st.session_state.show_results = False
if 'portfolio_results' not in st.session_state: st.session_state.portfolio_results = pd.DataFrame()
# '포트폴리오 선택'은 04_dashboard.py에서 초기화될 수 있으므로, 없으면 빈 리스트로 초기화
if '포트폴리오 선택' not in st.session_state: st.session_state['포트폴리오 선택'] = []


# 데이터 로드 및 전처리
df_full = load_and_process_data()

if df_full.empty:
    st.info("데이터 로드에 실패했거나 처리할 종목이 없습니다.")
    st.stop()

# --- 필터, 정렬 및 검색 옵션 Expander ---
with st.expander("🔍 필터, 정렬 및 검색 옵션", expanded=True):
    col_filter, col_sort1, col_sort2 = st.columns(3)
    
    with col_filter:
        # target_class를 기준으로 필터링
        target_class_options_map = {
            "전체 보기": [0,1,2,3],
            "안정형 (target_class 0)": [0],
            "위험중립형 (target_class 1)": [1],
            "적극투자형 (target_class 2)": [2],
            "공격투자형 (target_class 3)": [3]
        }
        selected_target_class_label = st.selectbox("투자성향 분류 필터", 
                                                options=list(target_class_options_map.keys()),
                                                index=0) # 기본값: '전체 보기'
    
    selected_target_classes = target_class_options_map[selected_target_class_label]
    filtered_df = df_full[df_full['target_class'].isin(selected_target_classes)].copy()

    # 정렬 기준 옵션 추가 (배당수익률 제거)
    sort_option_map = {'기본 (회사명 순)': '회사명'}
    if '초과수익률_apply' in filtered_df.columns: sort_option_map['초과수익률'] = '초과수익률_apply'
    if 'CAGR' in filtered_df.columns: sort_option_map['CAGR'] = 'CAGR'
    if '연간변동성' in filtered_df.columns: sort_option_map['연간변동성'] = '연간변동성'

    with col_sort1:
        sort_by_label = st.selectbox("정렬 기준", options=list(sort_option_map.keys()))
    sort_by_col = sort_option_map[sort_by_label]

    with col_sort2:
        # 기본 정렬 순서 설정 (수익률 등은 내림차순, 변동성 등은 오름차순)
        is_desc_default = sort_by_col in ['초과수익률_apply', 'CAGR'] # 배당수익률 제거
        is_asc_default = sort_by_col in ['연간변동성']

        if is_desc_default:
            default_index_sort = 1 # '내림차순'
        elif is_asc_default:
            default_index_sort = 0 # '오름차순'
        else:
            default_index_sort = 0 # 기타(회사명)는 '오름차순'
        
        ascending = st.radio("정렬 순서", ('오름차순', '내림차순'), 
                             index=default_index_sort,
                             horizontal=True, key='sort_order_general_stock_page') 
    
    is_ascending = (ascending == '오름차순')
    filtered_df = filtered_df.sort_values(by=sort_by_col, ascending=is_ascending)

st.markdown("---")
st.subheader(f"필터링된 종목 리스트 ({len(filtered_df)}개)")

# 검색 및 상위 5개/모두 해제 버튼
col_search, col_btn1, col_btn2 = st.columns([2, 1, 1])
with col_search:
    search_query = st.text_input("종목명 검색", placeholder="종목명 일부를 입력하세요...", label_visibility="collapsed")

if search_query:
    df_to_display = filtered_df[filtered_df['회사명'].str.contains(search_query, case=False, na=False)]
else:
    df_to_display = filtered_df

with col_btn1:
    if st.button("✨ 상위 5개 추가 선택", use_container_width=True):
        top_5_stocks = df_to_display.head(5)['회사명'].tolist()
        # 기존 선택에 추가 (중복 방지)
        st.session_state['포트폴리오 선택'] = list(set(st.session_state['포트폴리오 선택'] + top_5_stocks))
        st.rerun()
with col_btn2:
    if st.button("🔄 선택 모두 해제", use_container_width=True):
        st.session_state['포트폴리오 선택'] = []
        st.rerun()

st.info("💡 **'상위 5개 추가 선택' 버튼은 현재 보이는 리스트의 정렬 순서를 따르며, 기존 선택에 추가됩니다.**")

if df_to_display.empty:
    st.warning("표시할 종목이 없습니다. 필터 조건을 조정하거나 검색어를 확인해주세요.")
else:
    # 대시보드 테이블에 표시할 컬럼 정의 (배당수익률 제거)
    cols_to_display_table = ['회사명', '거래소코드', 'CAGR', '연간변동성', '초과수익률_apply', 'target_class']
    final_display_cols_table = [col for col in cols_to_display_table if col in df_to_display.columns]
    
    display_df = df_to_display[final_display_cols_table].copy()
    display_df.insert(0, '선택', False)
    display_df['선택'] = display_df['회사명'].isin(st.session_state['포트폴리오 선택'])

    # 컬럼 이름 변경 (사용자에게 더 친숙하게) (배당수익률 제거)
    display_df.columns = ['선택', '회사명', '거래소코드', 'CAGR (%)', '연간변동성 (%)', '초과수익률 (%)', '투자성향분류']

    edited_df = st.data_editor(
        display_df, 
        column_config={"선택": st.column_config.CheckboxColumn(required=True)}, 
        disabled=display_df.columns.drop('선택'), # '선택' 컬럼만 편집 가능하게 함
        hide_index=True, 
        use_container_width=True
    )
    # 사용자가 체크박스를 조작한 결과를 세션 상태에 반영
    st.session_state['포트폴리오 선택'] = edited_df[edited_df['선택']]['회사명'].tolist()

# 선택된 종목으로 포트폴리오 분석
# df_full에서 선택된 종목의 전체 데이터를 가져옴 (필터링된 df_to_display가 아닌 원본에서)
selected_stocks_df = df_full[df_full['회사명'].isin(st.session_state['포트폴리오 선택'])].copy()
num_selected = len(selected_stocks_df)
st.markdown("---")

is_disabled = (num_selected == 0)
if st.button('📈 포트폴리오 분석 실행', type='primary', use_container_width=True, disabled=is_disabled):
    if '초과수익률_apply' in selected_stocks_df.columns:
        st.session_state.portfolio_results = selected_stocks_df.copy()
        st.session_state.show_results = True
    else:
        st.error("⚠️ 분석에 필요한 '초과수익률_apply' 컬럼이 데이터에 없습니다. 데이터셋을 확인해주세요.")
        st.session_state.show_results = False
    st.rerun()

if num_selected == 0:
    st.session_state.show_results = False
    st.warning("**분석할 종목을 1개 이상 선택해주세요.**")

st.markdown("---")
st.header("📊 현재 선택된 포트폴리오 분석 결과")
if st.session_state.show_results:
    results_df = st.session_state.portfolio_results
    if not results_df.empty:
        benchmark_rate = 2.8 # 예시 국고채 금리
        
        # 포트폴리오의 총 초과수익률은 선택된 종목들의 평균 초과수익률로 계산
        if '초과수익률_apply' in results_df.columns:
            average_excess_return = results_df['초과수익률_apply'].mean()
        else:
            average_excess_return = 0
            st.warning("'초과수익률_apply' 컬럼이 없어 포트폴리오 수익률을 계산할 수 없습니다.")

        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            st.subheader("✅ 포트폴리오 성과 요약")
            st.metric(label=f"평균 초과수익률 (vs 국고채 {benchmark_rate}%)", value=f"{average_excess_return:.2f} %p")
            st.markdown(f"**선택된 종목 수:** {len(results_df)}개")
            
            # 선택된 종목들의 주요 정보를 표로 제공 (배당수익률 제거)
            summary_cols = ['회사명', '초과수익률_apply', 'CAGR', '연간변동성', 'target_class']
            summary_display_df = results_df[[col for col in summary_cols if col in results_df.columns]].copy()
            summary_display_df.columns = ['회사명', '초과수익률 (%)', 'CAGR (%)', '연간변동성 (%)', '투자성향분류']
            st.dataframe(summary_display_df, hide_index=True, use_container_width=True)

        with col_res2:
            if '초과수익률_apply' in results_df.columns:
                st.subheader(f"📊 선택된 종목별 초과수익률")
                fig = px.bar(results_df, x='회사명', y='초과수익률_apply', 
                             color='초과수익률_apply', 
                             color_continuous_scale=px.colors.diverging.RdYlGn, 
                             color_continuous_midpoint=0,
                             title="선택 종목별 초과수익률") 
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("초과수익률 데이터를 시각화할 수 없습니다.")
    else:
        st.info("선택된 종목이 없습니다. 위에서 종목을 선택하고 '포트폴리오 분석 실행' 버튼을 눌러주세요.")
else:
    st.info("위 표에서 종목을 선택하고 '포트폴리오 분석 실행' 버튼을 누르면 이곳에 결과가 표시됩니다.")

st.markdown("---")

# 변경된 부분: 버튼 위치 교환 (설문 돌아가기가 왼쪽, 추천 펀드 페이지 돌아가기가 오른쪽)
col_back_to_survey, col_back_to_fund = st.columns(2) 
with col_back_to_survey: # 설문 페이지로 돌아가기 (왼쪽)
    if st.button("🏠 설문 페이지로 돌아가기", use_container_width=True):
        reset_survey_state() # 상태 초기화 함수 호출
        st.switch_page("pages/01_questionnaire.py")
with col_back_to_fund: # 추천 펀드 페이지로 돌아가기 (오른쪽)
    if st.button("💰 추천 펀드 페이지로 돌아가기", use_container_width=True):
        st.switch_page("pages/04_dashboard.py")