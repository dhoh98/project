# pages/04_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_and_process_data

st.set_page_config(page_title="종목 대시보드", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stColumnSortIcon"] { display: none; }
    </style>
    """, unsafe_allow_html=True)
st.title("📈 맞춤형 종목 필터링 대시보드")

if 'show_results' not in st.session_state: st.session_state.show_results = False
if 'portfolio_results' not in st.session_state: st.session_state.portfolio_results = pd.DataFrame()
if '포트폴리오 선택' not in st.session_state: st.session_state['포트폴리오 선택'] = []

df_full = load_and_process_data()
if not df_full.empty:
    df_full = df_full[df_full['위험도'] != 2].copy()
if df_full.empty:
    st.info("처리할 데이터가 없습니다.")
    st.stop()
df = df_full.loc[df_full.groupby('거래소코드')['회계년도'].idxmax()].copy()

with st.expander("🔍 필터, 정렬 및 검색 옵션", expanded=True):
    def get_default_risk_level():
        investment_type = st.session_state.get('investment_type', '위험중립형')
        if investment_type in ["안정형", "안정추구형"]: return '저위험'
        elif investment_type == "위험중립형": return '중위험'
        else: return '중위험'
    
    col_filter, col_sort1, col_sort2 = st.columns(3)
    with col_filter:
        risk_level_options = ['저위험', '중위험', '전체 보기']
        default_risk_label = get_default_risk_level()
        try: default_index = risk_level_options.index(default_risk_label)
        except ValueError: default_index = 2
        selected_risk_label = st.selectbox("위험 등급", options=risk_level_options, index=default_index)
    
    risk_level_map = {'저위험': [0], '중위험': [1], '전체 보기': [0, 1]}
    selected_risk_codes = risk_level_map[selected_risk_label]
    filtered_df = df[df['위험도'].isin(selected_risk_codes)].copy()

    sort_option_map = {'기본 (회사명 순)': '회사명'}
    if '배당수익률' in filtered_df.columns: sort_option_map['배당수익률'] = '배당수익률'
    if '초과수익률_apply' in filtered_df.columns: sort_option_map['초과수익률'] = '초과수익률_apply'
    
    with col_sort1:
        sort_by_label = st.selectbox("정렬 기준", options=list(sort_option_map.keys()))
    sort_by_col = sort_option_map[sort_by_label]
    with col_sort2:
        is_desc_default = sort_by_col in ['배당수익률', '초과수익률_apply']
        ascending = st.radio("정렬 순서", ('오름차순', '내림차순'), index=1 if is_desc_default else 0, horizontal=True, key='sort_order')
    
    is_ascending = (ascending == '오름차순')
    filtered_df = filtered_df.sort_values(by=sort_by_col, ascending=is_ascending)

st.markdown("---")
st.header(f"'{selected_risk_label}' 종목 리스트")
col_search, col_btn1, col_btn2 = st.columns([2, 1, 1])
with col_search:
    search_query = st.text_input("종목명 검색", placeholder="종목명 일부를 입력하세요...", label_visibility="collapsed")

if search_query:
    df_to_display = filtered_df[filtered_df['회사명'].str.contains(search_query, case=False, na=False)]
else:
    df_to_display = filtered_df

with col_btn1:
    if st.button("✨ 상위 5개 선택", use_container_width=True):
        top_5_stocks = df_to_display.head(5)['회사명'].tolist()
        st.session_state['포트폴리오 선택'] = top_5_stocks
        st.rerun()
with col_btn2:
    if st.button("🔄 모두 해제", use_container_width=True):
        st.session_state['포트폴리오 선택'] = []
        st.rerun()

st.info("💡 **'상위 5개 선택' 버튼은 현재 보이는 리스트의 정렬 순서를 따릅니다.**")
if df_to_display.empty:
    st.warning("표시할 종목이 없습니다.")
else:
    cols_to_display = ['회사명', '거래소코드', '배당수익률', '초과수익률_apply']
    final_display_cols = [col for col in cols_to_display if col in df_to_display.columns]
    display_df = df_to_display[final_display_cols].copy()
    display_df.insert(0, '선택', False)
    display_df['선택'] = display_df['회사명'].isin(st.session_state['포트폴리오 선택'])
    edited_df = st.data_editor(display_df, column_config={"선택": st.column_config.CheckboxColumn(required=True)}, disabled=display_df.columns.drop('선택'), hide_index=True, use_container_width=True)
    st.session_state['포트폴리오 선택'] = edited_df[edited_df['선택']]['회사명'].tolist()

selected_stocks_df = filtered_df[filtered_df['회사명'].isin(st.session_state['포트폴리오 선택'])]
num_selected = len(selected_stocks_df)
st.markdown("---")
is_disabled = (num_selected == 0)
if st.button('📈 포트폴리오 분석 실행', type='primary', use_container_width=True, disabled=is_disabled):
    if '초과수익률_apply' in selected_stocks_df.columns:
        st.session_state.portfolio_results = selected_stocks_df.copy()
        st.session_state.show_results = True
    else:
        st.error("⚠️ 분석에 필요한 '초과수익률_apply' 컬럼이 데이터에 없습니다.")
        st.session_state.show_results = False
if num_selected == 0:
    st.session_state.show_results = False
    st.warning("**분석할 종목을 1개 이상 선택해주세요.**")

st.markdown("---")
st.header("📊 포트폴리오 분석 결과")
if st.session_state.show_results:
    results_df = st.session_state.portfolio_results
    if not results_df.empty:
        benchmark_rate = 2.8
        total_excess_return = results_df['초과수익률_apply'].sum()
        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            st.subheader("✅ 포트폴리오 성과")
            st.metric(label=f"총 초과수익률 (vs 국고채 {benchmark_rate}%)", value=f"{total_excess_return:.2f} %p")
        with col_res2:
            st.subheader(f"📊 선택된 {len(results_df)}개 종목별 초과수익률")
            fig = px.bar(results_df, x='회사명', y='초과수익률_apply', color='초과수익률_apply', color_continuous_scale=px.colors.diverging.RdYlGn, color_continuous_midpoint=0)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("위 표에서 종목을 선택하고 '분석 실행' 버튼을 누르면 이곳에 결과가 표시됩니다.")

st.markdown("---")
st.page_link("app.py", label="🏠 설문 페이지로 돌아가기", icon="📊")