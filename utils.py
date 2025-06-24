# utils.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- 설문 관련 함수 및 데이터 ---

questions = {
    "age": {
        "title": "1. 당신의 연령대는 어떻게 됩니까?",
        "options": ["19세 이하", "20세~40세", "41세~50세", "51세~60세", "61세 이상"],
        "scores": [12.5, 12.5, 9.3, 6.2, 3.1]
    },
    "investment_period": {
        "title": "2. 투자하고자 하는 자금의 투자 가능 기간은 얼마나 됩니까?",
        "options": ["6개월 이내", "6개월 이상~1년 이내", "1년 이상~2년 이내", "2년 이상~3년 이내", "3년 이상"],
        "scores": [3.1, 6.2, 9.3, 12.5, 15.6]
    },
    "investment_experience": {
        "title": "3. 다음 중 투자경험과 가장 가까운 것은 어느 것입니까? (중복 가능)",
        "options": [
            "은행의 예·적금, 국채, 지방채, 보증채, MMF, CMA 등",
            "금융채, 신용도가 높은 회사채, 채권형펀드, 원금보존추구형ELS 등",
            "신용도 중간 등급의 회사채, 원금의 일부만 보장되는 ELS, 혼합형펀드 등",
            "신용도가 낮은 회사채, 주식, 원금이 보장되지 않는 ELS, 시장수익률 수준의 수익을 추구하는 주식형펀드 등",
            "ELW, 선물옵션, 시장수익률 이상의 수익을 추구하는 주식형펀드, 파생상품에 투자하는 펀드, 주식 신용거래 등"
        ],
        "scores": [3.1, 6.2, 9.3, 12.5, 15.6]
    },
    "knowledge_level": {
        "title": "4. 금융상품 투자에 대한 본인의 지식수준은 어느 정도라고 생각하십니까?",
        "options": [
            "[매우 낮은 수준] 투자의사 결정을 스스로 내려본 경험이 없는 정도",
            "[낮은 수준] 주식과 채권의 차이를 구별할 수 있는 정도",
            "[높은 수준] 투자할 수 있는 대부분의 금융상품의 차이를 구별할 수 있는 정도",
            "[매우 높은 수준] 금융상품을 비롯하여 모든 투자대상 상품의 차이를 이해할 수 있는 정도"
        ],
        "scores": [3.1, 6.2, 9.3, 12.5]
    },
    "asset_ratio": {
        "title": "5. 현재 투자하고자 하는 자금은 전체 금융자산(부동산 등을 제외) 중 어느 정도의 비중을 차지합니까?",
        "options": ["10% 이내", "10% 이상~20% 이내", "20% 이상~30% 이내", "30% 이상~40% 이내", "40% 이상"],
        "scores": [15.6, 12.5, 9.3, 6.2, 3.1]
    },
    "income_source": {
        "title": "6. 다음 중 당신의 수입원을 가장 잘 나타내고 있는 것은 어느 것입니까?",
        "options": [
            "현재 일정한 수입이 발생하고 있으며, 향후 현재 수준을 유지하거나 증가할 것으로 예상된다.",
            "현재 일정한 수입이 발생하고 있으나, 향후 감소하거나 불안정할 것으로 예상된다.",
            "현재 일정한 수입이 없으며, 연금이 주수입원이다."
        ],
        "scores": [9.3, 6.2, 3.1]
    },
    "risk_tolerance": {
        "title": "7. 만약 투자원금에 손실이 발생할 경우 다음 중 감수할 수 있는 손실 수준은 어느 것입니까?",
        "options": [
            "무슨 일이 있어도 투자원금은 보전되어야 한다.",
            "10% 미만까지는 손실을 감수할 수 있을 것 같다.",
            "20% 미만까지는 손실을 감수할 수 있을 것 같다.",
            "기대수익이 높다면 위험이 높아도 상관하지 않겠다."
        ],
        "scores": [-6.2, 6.2, 12.5, 18.7]
    }
}

def calculate_score(answers):
    total_score = 0
    score_breakdown = {}
    for key, answer in answers.items():
        if answer is None: continue
        question = questions[key]
        if key == "investment_experience":
            score = max([question['scores'][i] for i in answer]) if answer else 0
        else:
            score = question['scores'][answer]
        score_breakdown[key] = score
        total_score += score
    return total_score, score_breakdown

def classify_investment_type(score):
    if score <= 20: return "안정형", "#4CAF50"
    elif score <= 40: return "안정추구형", "#8BC34A"
    elif score <= 60: return "위험중립형", "#FFC107"
    elif score <= 80: return "적극투자형", "#FF9800"
    else: return "공격투자형", "#F44336"

def validate_answers():
    errors = set()
    for key in questions.keys():
        if key not in st.session_state.answers or st.session_state.answers[key] is None:
            errors.add(key)
        elif key == "investment_experience" and not st.session_state.answers[key]:
            errors.add(key)
    st.session_state.validation_errors = errors
    return len(errors) == 0

def show_footer():
    st.markdown("---")
    st.markdown("💡 **주의사항**: 본 진단 결과는 참고용이며, 실제 투자 결정 시에는 전문가와 상담하시기 바랍니다.")

# --- 대시보드 데이터 로딩 함수 ---

@st.cache_data
def load_and_process_data(file_path='dataset1.xlsx'):
    try:
        df = pd.read_excel(file_path, dtype={'거래소코드': str})
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다.")
        return pd.DataFrame()

    df.sort_values(by=['거래소코드', '회계년도'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    col_c1, col_c2 = '이자보상배율(이자비용)', '영업활동으로 인한 현금흐름(간접법)(*)(천원)'
    if col_c1 not in df.columns or col_c2 not in df.columns:
        st.error("필요한 컬럼이 파일에 없습니다.")
        return pd.DataFrame()

    df['C1_flag'] = (df[col_c1].fillna(999) < 1).astype(int)
    df['C2_flag'] = (df[col_c2].fillna(9999) < 0).astype(int)
    df['C1_3yr_sum'] = df.groupby('거래소코드')['C1_flag'].rolling(window=3, min_periods=3).sum().reset_index(level=0, drop=True)
    df['C2_3yr_sum'] = df.groupby('거래소코드')['C2_flag'].rolling(window=3, min_periods=3).sum().reset_index(level=0, drop=True)
    df['C1_met'] = (df['C1_3yr_sum'] == 3)
    df['C2_met'] = (df['C2_3yr_sum'] == 3)

    conditions = [(df['C1_met'] == True) & (df['C2_met'] == True), (df['C1_met'] == True) | (df['C2_met'] == True)]
    choices = [2, 1]
    df['위험도'] = np.select(conditions, choices, default=0)
    df.loc[df['C1_3yr_sum'].isnull() | df['C2_3yr_sum'].isnull(), '위험도'] = np.nan

    final_df = df.dropna(subset=['위험도']).copy()
    final_df['위험도'] = final_df['위험도'].astype(int)

    if '배당수익률' not in final_df.columns:
        np.random.seed(42)
        final_df['배당수익률'] = np.random.uniform(0.5, 7.0, size=len(final_df)).round(2)

    if '초과수익률_apply' not in final_df.columns and '배당수익률' in final_df.columns:
         final_df['초과수익률_apply'] = (final_df['배당수익률'] - 2.8).round(2)

    risk_map = {0: '저위험', 1: '중위험', 2: '고위험'}
    final_df['위험도_라벨'] = final_df['위험도'].map(risk_map)

    final_df.drop(columns=['C1_flag', 'C2_flag', 'C1_3yr_sum', 'C2_3yr_sum', 'C1_met', 'C2_met'], inplace=True, errors='ignore')

    return final_df