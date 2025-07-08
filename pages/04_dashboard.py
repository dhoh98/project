import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import numpy as np 
# classify_investment_type을 import할 필요가 없습니다. (utils.py의 classify_investment_type은 점수를 인자로 받으므로)
# 대신, utils.py의 classify_investment_type이 반환하는 색상 매핑을 여기에 직접 정의하여 사용합니다.
from utils import load_and_process_data, reset_survey_state 

# 페이지 설정
st.set_page_config(page_title="추천 펀드", page_icon="💰", layout="wide")

# --- 모든 페이지 공통 UI 숨김 CSS (이전과 동일) ---
st.markdown("""
    <style>
        /* CSS styles remain the same */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: block; }
        
        [data-testid="stColumnSortIcon"] { display: none; } 

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

# --- 직접 접근 방지 로직 (이전과 동일) ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()

# --- 백테스팅 결과 차트 생성 함수 (모든 클래스) ---
def create_backtest_results_chart(backtest_results, investment_type): # investment_type 인자 추가
    """
    백테스팅 결과를 막대 차트로 시각화합니다.
    사용자 투자성향에 맞는 클래스 그룹만 색깔을 표시하고 나머지는 흑백으로 합니다.
    """
    if not backtest_results:
        return go.Figure()
    
    # investment_type에 따라 사용할 '조건 그룹'을 매핑
    # 이 맵은 backtest_results의 key (Class X (QY))를 찾아내기 위함
    investment_group_map_for_chart = { # 이름 변경 (충돌 방지)
        '안정형': 'Class 0 (Q1)', 
        '안정추구형': 'Class 0 (Q1)', 
        '위험중립형': 'Class 1 (Q1~Q2)', 
        '적극투자형': 'Class 2 (Q1~Q3)', 
        '공격투자형': 'Class 3 (Q1~Q4)',
    }
    # Class Label을 클래스 번호로 매핑 (X축 라벨에 사용)
    class_to_number_map = {
        'Class 0 (Q1)': '0', 
        'Class 1 (Q1~Q2)': '1', 
        'Class 2 (Q1~Q3)': '2', 
        'Class 3 (Q1~Q4)': '3' 
    }

    selected_group_label_for_chart = investment_group_map_for_chart.get(investment_type, 'Class 2 (Q1~Q3)') # 사용자의 유형에 맞는 Class (예: Class 0 (Q1))

    # 데이터 준비: 연도, 클래스 라벨, 평균 CAGR 추출 및 정렬
    chart_data = []
    sorted_keys = sorted(backtest_results.keys()) 
    for key in sorted_keys:
        year, label_raw = key.split(' - ')
        # Class 3을 제외하고 Class 0, 1, 2만 포함
        if 'Class 3' not in label_raw:
            chart_data.append({'Year': year, 'Label_Raw': label_raw, 'CAGR': backtest_results[key]['mean_cagr']}) 
    
    df_chart = pd.DataFrame(chart_data)
    
    # 정렬 키는 Class N (Qx) 형태의 원본 레이블에 따라 정렬 (논리적 순서)
    label_sort_map = {'Class 0 (Q1)': 0, 'Class 1 (Q1~Q2)': 1, 'Class 2 (Q1~Q3)': 2, 'Class 3 (Q1~Q4)': 3}
    df_chart['Label_Sort_Key'] = df_chart['Label_Raw'].map(label_sort_map)
    df_chart.sort_values(by=['Year', 'Label_Sort_Key'], inplace=True)
    
    # X축 라벨을 "년도/클래스번호" 형식으로 변경 (예: 2017/0, 2017/1, 2018/0...)
    labels = [f"{row['Year']}/{class_to_number_map.get(row['Label_Raw'], '?')}" for idx, row in df_chart.iterrows()] 
    # CAGR 값을 6으로 나누어 연평균으로 변환
    values = [cagr / 6 if pd.notna(cagr) and cagr != 0 else 0.0 for cagr in df_chart['CAGR'].tolist()]

    # 막대 색상 결정 로직 (사용자 선택 그룹만 컬러, 나머지는 회색)
    bar_colors = []
    for label_raw_from_df in df_chart['Label_Raw']: 
        if label_raw_from_df == selected_group_label_for_chart: # 사용자가 선택한 (Class X (QY)) 그룹에 해당하는 막대
            if 'Class 0' in label_raw_from_df:
                bar_colors.append('#4CAF50')  
            elif 'Class 1' in label_raw_from_df:
                bar_colors.append('#ffc107')  
            elif 'Class 2' in label_raw_from_df:
                bar_colors.append('#FF9800')  
            elif 'Class 3' in label_raw_from_df:
                bar_colors.append('#F44336')  
            else: 
                bar_colors.append('#9E9E9E') 
        else: 
            bar_colors.append('#CCCCCC') 
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels, 
            y=values,
            marker_color=bar_colors, 
            text=[f'{val:.2f}%' if pd.notna(val) else 'N/A' for val in values], 
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>연평균 CAGR: %{y:.2f}%<extra></extra>' 
        )
    ])
    
    fig.update_layout(
        title="📊 백테스팅 결과: 연도별 투자성향 그룹별 상위 10개 종목 연평균 CAGR",
        xaxis_title="연도/클래스", 
        yaxis_title="연평균 CAGR (%)",
        xaxis_tickangle=0, 
        xaxis_tickfont=dict(size=13), 
        height=600,
        showlegend=False,
        yaxis=dict(gridcolor='lightgray'),
        plot_bgcolor='white',
        margin=dict(t=80, b=120) 
    )
    
    return fig

# --- 백테스팅 로직을 포함하는 추천 종목 및 연도별 CAGR 계산 함수 ---
@st.cache_data(ttl=3600) # 데이터 처리 결과를 캐싱하여 성능 향상 (1시간 TTL)
def get_backtested_results_and_latest_recommendations(df_full_cached, investment_type_cached):
    """
    각 연도별, 각 조건 그룹별 상위 10개 종목을 찾고, 그들의 평균 CAGR을 계산합니다.
    또한, 특정 investment_type에 해당하는 최신 연도의 추천 종목 목록을 반환합니다.
    recommended_stocks는 이제 각 종목의 회사명과 CAGR을 포함하는 딕셔너리 리스트입니다.

    반환:
        - results_all_conditions (dict): {f"{year} - {label}": {'mean_cagr': float, 'recommended_stocks': list of dicts}} 형태
        - latest_recommendations_for_type (pd.DataFrame): 사용자의 investment_type에 맞는 최신 연도 추천 종목
    """
    df_full = df_full_cached.copy()

    # investment_type (한글 유형명)에 따라 사용할 '조건 그룹'을 매핑
    # 이 맵은 get_backtested_results_and_latest_recommendations 함수 내부에서
    # 'selected_group_label'을 결정하고, 'latest_recommendations_for_type'을 필터링하는 데 사용됩니다.
    investment_group_map = {
        '안정추구형': 'Class 0 (Q1)',
        '위험중립형': 'Class 1 (Q1~Q2)',
        '적극투자형': 'Class 2 (Q1~Q3)',
        '공격투자형': 'Class 3 (Q1~Q4)',
        # '안정형'은 이 대시보드 페이지에 오지 않으므로 여기에 매핑하지 않습니다.
    }
    
    if '회계년도' not in df_full.columns:
        st.error("⚠️ 데이터에 '회계년도' 컬럼이 없습니다. 데이터 구조를 확인해주세요.")
        return {}, pd.DataFrame(columns=['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class'])

    df_full['회계년도'] = pd.to_numeric(df_full['회계년도'], errors='coerce').astype('Int64')
    df_full.dropna(subset=['회계년도'], inplace=True) 

    all_years = sorted(df_full['회계년도'].unique().tolist())
    if not all_years:
        st.warning("⚠️ '회계년도' 데이터가 유효하지 않아 백테스팅을 수행할 수 없습니다.")
        return {}, pd.DataFrame(columns=['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class'])

    latest_year = all_years[-1]

    results_all_conditions = {} 
    latest_recommendations_for_type = pd.DataFrame(columns=['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class']) 

    company_name_col = None
    possible_company_cols = ['회사명', '종목명', '회사', '종목', 'Company', 'Name']
    for col in possible_company_cols:
        if col in df_full.columns:
            company_name_col = col
            break
    
    if company_name_col is None:
        st.error("⚠️ 회사명을 나타내는 컬럼을 찾을 수 없습니다. 가능한 컬럼명: " + ", ".join(possible_company_cols))
        return {}, pd.DataFrame(columns=['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class'])


    conditions_definitions = {
        'Class 0 (Q1)': (lambda df_y: (df_y['target_class'] == 0) & (df_y['vol_quartile'] == 1)),
        'Class 1 (Q1~Q2)': (lambda df_y: (df_y['target_class'].isin([0, 1])) & (df_y['vol_quartile'].isin([1, 2]))),
        'Class 2 (Q1~Q3)': (lambda df_y: (df_y['target_class'].isin([0, 1, 2])) & (df_y['vol_quartile'].isin([1, 2, 3]))),
        'Class 3 (Q1~Q4)': (lambda df_y: (df_y['target_class'].isin([0, 1, 2, 3])) & (df_y['vol_quartile'].isin([1, 2, 3, 4]))),
    }

    for year in all_years:
        df_year = df_full[df_full['회계년도'] == year].copy()

        required_cols_for_processing = ['target_class', 'vol_quartile', 'CAGR', '거래소코드', '연간변동성'] 
        if company_name_col:
            required_cols_for_processing.append(company_name_col)

        # 필수 컬럼이 하나라도 누락된 연도는 건너뛰고 빈 결과로 채움
        if not all(col in df_year.columns for col in required_cols_for_processing):
            for label in conditions_definitions.keys():
                key = f"{year} - {label}"
                results_all_conditions[key] = {'mean_cagr': 0.0, 'recommended_stocks': []} 
            continue 

        for label, condition_func in conditions_definitions.items():
            key = f"{year} - {label}"
            
            condition_mask = condition_func(df_year)
            filtered_df = df_year[condition_mask]
            
            mean_cagr = 0.0
            top10_stocks_details = [] 
            current_top10_cagr_df = pd.DataFrame(columns=['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class']) 

            if not filtered_df.empty:
                filtered_df.loc[:, 'CAGR'] = pd.to_numeric(filtered_df['CAGR'], errors='coerce')
                
                # '회사명'과 'CAGR' 컬럼이 모두 존재하며 유효한 데이터가 있는 경우만 처리
                if company_name_col in filtered_df.columns and 'CAGR' in filtered_df.columns and not filtered_df.dropna(subset=[company_name_col, 'CAGR']).empty:
                    current_top10_cagr_df = filtered_df.sort_values(by='CAGR', ascending=False, na_position='last').head(10)
                    
                    mean_cagr = current_top10_cagr_df['CAGR'].mean()
                    if pd.isna(mean_cagr):
                        mean_cagr = 0.0
                    
                    # 회사명과 CAGR을 포함하는 딕셔너리 리스트 생성
                    # 회사명 컬럼 이름을 '회사명'으로 통일하여 to_dict에 전달
                    temp_df_for_details_conversion = current_top10_cagr_df[[company_name_col, 'CAGR']].copy()
                    if company_name_col != '회사명':
                        temp_df_for_details_conversion.rename(columns={company_name_col: '회사명'}, inplace=True)
                    
                    # NaN 값이 있는 행은 드롭하여 깨끗한 데이터만 남김 (회사명, CAGR 둘 다 유효한 경우)
                    top10_stocks_details = temp_df_for_details_conversion.dropna(subset=['회사명', 'CAGR']).to_dict(orient='records')
                else: # 회사명이나 CAGR 컬럼이 없거나, 유효한 데이터가 하나도 없는 경우
                    top10_stocks_details = []
                    mean_cagr = 0.0 # 계산 불가
            
            results_all_conditions[key] = {
                'mean_cagr': mean_cagr,
                'recommended_stocks': top10_stocks_details 
            }

            # 최신 연도 추천 종목을 저장하는 부분은 이미 잘 되어있었음
            # 이 부분에서 investment_type_cached는 classify_investment_type이 반환하는 실제 유형명입니다.
            # 이 유형명이 investment_group_map에 정의된 Class X (QY) 라벨로 변환되어 비교됩니다.
            if year == latest_year and label == investment_group_map.get(investment_type_cached):
                cols_for_latest_rec = ['회사명', '거래소코드', 'CAGR', '연간변동성', 'target_class']
                # current_top10_cagr_df가 비어있을 수 있으므로 빈 DataFrame으로 기본값 설정
                if current_top10_cagr_df.empty:
                    latest_recommendations_for_type = pd.DataFrame(columns=cols_for_latest_rec)
                else:
                    latest_recommendations_for_type = current_top10_cagr_df[[col for col in cols_for_latest_rec if col in current_top10_cagr_df.columns]].copy()
                    if company_name_col != '회사명' and company_name_col in latest_recommendations_for_type.columns:
                        latest_recommendations_for_type.rename(columns={company_name_col: '회사명'}, inplace=True)
    
    return results_all_conditions, latest_recommendations_for_type


# --- 벤치마크 꺾은선 그래프 표현 함수 (수정 없음) ---
# df_recommended_yearly_cagr은 사용자의 투자성향에 맞는 데이터만 포함한 DataFrame입니다.
def create_benchmark_chart(df_recommended_yearly_cagr, investment_type): 
    """
    추천 펀드의 연도별 CAGR 평균과 벤치마크를 비교하는 차트를 생성합니다.
    모든 데이터는 꺾은선으로 표시하며, 하나의 Y축을 공유하고 범위는 -50%에서 200%로 고정됩니다.
    """
    if df_recommended_yearly_cagr.empty:
        st.warning(f"⚠️ {investment_type} 유형에 대한 연도별 CAGR 데이터가 없어 차트를 생성할 수 없습니다.")
        return go.Figure(), pd.DataFrame() 

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
    
    fig = go.Figure()
    
    # 1. 추천 펀드 CAGR (꺾은선 그래프)
    fig.add_trace(go.Scatter(
        x=df_recommended_yearly_cagr['회계년도'],
        y=df_recommended_yearly_cagr['추천 펀드'], 
        mode='lines+markers', 
        name=f'{investment_type} 추천 펀드',
        line=dict(color='#FF6B35', width=4), 
        marker=dict(symbol='diamond', size=10),
        hovertemplate='<b>연도:</b> %{x}<br><b>추천 펀드 CAGR:</b> %{y:.2f}%<extra></extra>'
    ))
    
    # 2. 벤치마크들 (꺾은선 그래프, 컬러 유지)
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
            hovertemplate=f'<b>연도:</b> %{{x}}<br><b>{col} 수익률:</b> %{{y:.2f}}%<extra></extra>'
        ))
    
    # 레이아웃 설정 (모든 선들이 하나의 Y축을 공유하며, 범위는 -50%에서 200%로 고정)
    fig.update_layout(
        title=f"📈 {investment_type} 유형 추천 펀드 vs 벤치마크 수익률 비교", 
        xaxis_title="연도",
        yaxis_title="수익률 (%)", 
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450, 
        yaxis=dict(
            side='left',
            showgrid=True,
            gridcolor='lightgray',
            autorange=False, # 자동 범위 설정 해제
            range=[-50, 200] # Y축 범위 고정: -50%에서 200%까지
        ),
        plot_bgcolor='white'
    )
    
    return fig, df_benchmark


# --- 페이지 시작 ---
st.title("💰 투자성향 맞춤 추천 펀드")

# 여기서 투자 성향과 색상 코드를 함께 가져옵니다.
# pages/03_result.py에서 st.session_state['total_score']와 st.session_state['investment_type']이 저장되어 있어야 합니다.
retrieved_investment_type = st.session_state.get('investment_type', '위험중립형') # 저장된 유형명 가져옴

# utils.py의 classify_investment_type 함수는 점수를 인자로 받으므로, 
# 여기서는 직접 색상 매핑 딕셔너리를 사용하여 동적 색상을 적용합니다.
# 이 매핑은 utils.py의 classify_investment_type 함수와 동일해야 합니다.
investment_type_color_map = {
    "안정형": "#4CAF50",
    "안정추구형": "#8BC34A",
    "위험중립형": "#FFC107",
    "적극투자형": "#FF9800",
    "공격투자형": "#F44336"
}
# 현재 투자성향에 맞는 색상 코드 찾기
current_investment_color = investment_type_color_map.get(retrieved_investment_type, "#9E9E9E") # 기본값 회색

# 안정형 사용자가 이 페이지에 도달했을 경우를 대비 (03_result.py에서 이미 막지만, 혹시 모를 상황 대비)
if retrieved_investment_type == '안정형':
    st.error("⚠️ '안정형' 투자자는 주식 종목 추천이 적합하지 않아 이 페이지에 접근할 수 없습니다.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()


st.markdown(f"### 🎉 회원님의 투자성향은 **<span style='color: {current_investment_color};'>{retrieved_investment_type}</span>** 입니다!", unsafe_allow_html=True) 
st.write(f"아래는 **{retrieved_investment_type}** 투자 성향에 맞춰 백테스팅된 펀드형 추천 포트폴리오의 결과입니다.")
st.markdown("---")

# 데이터 로드
df_full = load_and_process_data()

if df_full.empty:
    st.warning("데이터 로드에 실패했거나 처리할 종목이 없습니다.")
    st.stop()

if '연간변동성' in df_full.columns:
    df_full['연간변동성'] = pd.to_numeric(df_full['연간변동성'], errors='coerce')
    df_full.dropna(subset=['연간변동성'], inplace=True)
    
    if not df_full['연간변동성'].empty and df_full['연간변동성'].nunique() >= 4:
        df_full['vol_quartile'] = pd.qcut(df_full['연간변동성'], q=4, labels=[1, 2, 3, 4], duplicates='drop')
        df_full['vol_quartile'] = df_full['vol_quartile'].astype(int)
    else:
        st.warning("⚠️ '연간변동성' 데이터가 충분하지 않아 분위수(vol_quartile)를 계산할 수 없습니다. 분석이 제한될 수 있습니다.")
        df_full['vol_quartile'] = 1 
else:
    st.error("⚠️ 데이터에 '연간변동성' 컬럼이 없습니다. 데이터 구조를 확인해주세요.")
    st.stop()

if 'target_class' not in df_full.columns:
    st.error("⚠️ 데이터에 'target_class' 컬럼이 없습니다. 데이터 구조를 확인해주세요.")
    st.stop()


# --- 상태 초기화 (이전과 동일) ---
if 'animation_stage' not in st.session_state:
    st.session_state.animation_stage = 'initial'  

# 단계별 처리
if st.session_state.animation_stage == 'initial':
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ 지금 바로 회원님께 맞는 추천 펀드를 확인하세요! ✨</h3>", unsafe_allow_html=True)
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
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ 지금 바로 회원님께 맞는 추천 펀드를 확인하세요! ✨</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>선물 상자를 열고 있어요...</p>", unsafe_allow_html=True)
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
    
    # investment_type_cached 인자에 st.session_state에서 가져온 retrieved_investment_type을 전달합니다.
    if 'backtest_results_all_conditions' not in st.session_state or 'recommended_fund_stocks_latest' not in st.session_state:
        st.session_state.backtest_results_all_conditions, st.session_state.recommended_fund_stocks_latest = \
            get_backtested_results_and_latest_recommendations(df_full, retrieved_investment_type) 
    
    time.sleep(2.5)
    st.balloons()
    
    st.session_state.animation_stage = 'completed'
    st.rerun()

else:  # animation_stage == 'completed'
    st.markdown("<div class='slide-up'>", unsafe_allow_html=True)
    
    backtest_results_all_conditions = st.session_state.get('backtest_results_all_conditions', {})
    recommended_df_latest_year = st.session_state.get('recommended_fund_stocks_latest', pd.DataFrame())

    # investment_group_map 정의 (create_backtest_results_chart와 get_backtested_results_and_latest_recommendations에 전달될 것)
    # 이 맵은 Class 0 (Q1) 등 내부적인 라벨과 한글 투자성향 이름을 연결합니다.
    investment_group_map = {
        '안정형': 'Class 0 (Q1)', # 안정형은 이 대시보드에 오지 않지만, 혹시 모를 상황 대비 포함
        '안정추구형': 'Class 0 (Q1)', # 요청에 따라 안정추구형이 Class 0 (target_class=0)을 사용
        '위험중립형': 'Class 1 (Q1~Q2)', # 위험중립형이 Class 1 (target_class in [0,1])을 사용
        '적극투자형': 'Class 2 (Q1~Q3)', # 적극투자형이 Class 2 (target_class in [0,1,2])를 사용
        '공격투자형': 'Class 3 (Q1~Q4)', # 공격투자형이 Class 3 (target_class in [0,1,2,3])을 사용
    }
    # 실제 Chart 함수들에 넘길 selected_group_label은 retrieved_investment_type을 사용
    selected_group_label = investment_group_map.get(retrieved_investment_type, 'Class 2 (Q1~Q3)')


    # Move calculations for metrics here, as they are needed before the performance summary
    yearly_cagrs_for_metrics = [
        data['mean_cagr'] 
        for key, data in backtest_results_all_conditions.items() 
        if selected_group_label in key 
    ]
    overall_avg_cagr_recommended = pd.Series(yearly_cagrs_for_metrics).mean() if yearly_cagrs_for_metrics else 0.0
    if pd.isna(overall_avg_cagr_recommended):
        overall_avg_cagr_recommended = 0.0
    
    # 6년간 평균을 연평균으로 변환
    annual_avg_cagr_recommended = overall_avg_cagr_recommended / 6 if overall_avg_cagr_recommended != 0 else 0.0

    # `recommended_df_latest_year`가 비어있지 않은 경우에만 상세 정보 표시
    if not recommended_df_latest_year.empty:
        # --- 성과 요약 --- (FIRST)
        st.subheader(f"📊 {retrieved_investment_type} 유형 추천 펀드 성과 요약") # retrieved_investment_type 사용
        
        average_volatility = recommended_df_latest_year['연간변동성'].mean() if '연간변동성' in recommended_df_latest_year.columns else 0

        col1, col2 = st.columns(2) 
        with col1:
            st.metric(label="평균 연간복리수익률", value=f"{annual_avg_cagr_recommended:.2f} %")
        with col2:
            st.metric(label="평균 연간변동성 (최신 추천 종목 기준)", value=f"{average_volatility:.2f} %")
        
        st.info(f"💡 이 펀드는 회원님의 '{retrieved_investment_type}' 성향에 맞춰, 백테스팅된 **'{selected_group_label}'** 조건 그룹의 연도별 '연간변동성'과 'target_class' 기준에 부합하며 'CAGR'이 높은 상위 10개 종목으로 구성된 포트폴리오의 결과입니다.")
        
        st.markdown("---") 

        # --- 벤치마크 비교 차트 (SECOND) --- 
        st.subheader(f"📈 {retrieved_investment_type} 유형 추천 펀드 벤치마크 대비 성과 비교") # retrieved_investment_type 사용
        
        # create_benchmark_chart 함수에 필요한 df_recommended_yearly_cagr 생성
        df_recommended_yearly_cagr_for_benchmarking = pd.DataFrame([
            {'회계년도': year_key.split(' - ')[0], '추천 펀드': data['mean_cagr']}
            for year_key, data in backtest_results_all_conditions.items()
            if selected_group_label in year_key
        ])

        # create_benchmark_chart 함수 호출: 추천 펀드는 꺾은선, 벤치마크는 꺾은선 (모두 컬러, 단일 Y축)
        fig, benchmark_df = create_benchmark_chart(df_recommended_yearly_cagr_for_benchmarking, retrieved_investment_type) # retrieved_investment_type 전달
        st.plotly_chart(fig, use_container_width=True)
        
        # 벤치마크 평균 수익률 계산 및 표시
        # 값들을 미리 계산
        kospi_avg = benchmark_df['KOSPI'].mean()
        kosdaq_avg = benchmark_df['KOSDAQ'].mean()
        bond3y_avg = benchmark_df['국고채 3년'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: # 추천 펀드 6년간 CAGR (가장 먼저 표시)
            st.metric(
                label="추천 펀드 연평균 CAGR",
                value=f"{annual_avg_cagr_recommended:.2f}%",
                delta="기준"
            )
        with col2: # 국고채 3년 6년간 평균
            st.metric(
                label="국고채 3년 평균",
                value=f"{bond3y_avg:.2f}%",
                delta=f"{annual_avg_cagr_recommended - bond3y_avg:.2f}%p"
            )
        with col3: # KOSDAQ 6년간 평균
            st.metric(
                label="KOSDAQ 연평균",
                value=f"{kosdaq_avg:.2f}%",
                delta=f"{annual_avg_cagr_recommended - kosdaq_avg:.2f}%p"
            )
        with col4: # KOSPI 6년간 평균
            st.metric(
                label="KOSPI 연평균",
                value=f"{kospi_avg:.2f}%",
                delta=f"{annual_avg_cagr_recommended - kospi_avg:.2f}%p"
            )
        
        st.markdown("---") 

        # --- 1. 백테스팅 전체 결과 시각화 (THIRD) --- 
        st.subheader("📈 백테스팅 전체 결과") 
        backtest_fig = create_backtest_results_chart(backtest_results_all_conditions, retrieved_investment_type) # retrieved_investment_type 전달
        st.plotly_chart(backtest_fig, use_container_width=True)
        st.markdown("---") 

    else:
        # 이 경고 메시지에서도 investment_type 대신 retrieved_investment_type 사용
        st.warning(f"회원님의 '{retrieved_investment_type}' 투자성향에 맞는 최신 추천 종목을 찾지 못했습니다. 데이터가 부족하거나 조건이 너무 엄격합니다. 개별 종목 분석 페이지에서 직접 종목을 찾아보세요.")
    
    st.markdown("---")
    st.subheader("📋 다음 단계")

    col_survey_btn, col_stock_btn = st.columns(2) 
    with col_survey_btn:
        if st.button("🏠 설문 페이지로 돌아가기", use_container_width=True):
            st.session_state.animation_stage = 'initial'
            if 'backtest_results_all_conditions' in st.session_state:
                del st.session_state.backtest_results_all_conditions
            if 'recommended_fund_stocks_latest' in st.session_state:
                del st.session_state.recommended_fund_stocks_latest
            reset_survey_state()
            st.switch_page("pages/01_questionnaire.py")
    
            
    with col_stock_btn:
        # "로그아웃 하기" 버튼을 클릭하면 로그인 페이지로 이동하며 세션 초기화
        # type="secondary"를 사용하여 설문 페이지로 돌아가기 버튼과 색상을 구분합니다.
        if st.button("🚪 로그아웃 하기", type="secondary", use_container_width=True): # 버튼 레이블과 타입 변경
            st.session_state.logged_in = False # 로그인 상태를 False로 설정
            reset_survey_state() # 설문 및 대시보드 관련 모든 세션 상태 초기화
            # 포트폴리오 선택 내역은 reset_survey_state에서 이미 지워집니다.
            # st.session_state['포트폴리오 선택'] = [] 이 부분은 필요 없음
            st.switch_page("app.py") # 로그인 페이지로 이동
    
    st.markdown("</div>", unsafe_allow_html=True)
