import streamlit as st
import pandas as pd
import numpy as np

# --- 설문 관련 함수 및 데이터 (변경 없음) ---
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


# --- 설문 관련 세션 상태 초기화 함수 (최신 상태 반영) ---
def reset_survey_state():
    if 'answers' in st.session_state:
        del st.session_state.answers
    if 'survey_completed' in st.session_state:
        del st.session_state.survey_completed
    if 'validation_errors' in st.session_state:
        del st.session_state.validation_errors
    if 'investment_type' in st.session_state:
        del st.session_state.investment_type
    if 'total_score' in st.session_state:
        del st.session_state.total_score
    if 'score_breakdown' in st.session_state:
        del st.session_state.score_breakdown
    
    if 'portfolio_results' in st.session_state:
        del st.session_state.portfolio_results
    if 'show_results' in st.session_state:
        del st.session_state.show_results
    if '포트폴리오 선택' in st.session_state:
        del st.session_state['포트폴리오 선택']
    
    if 'initial_recommendation_loaded' in st.session_state:
        del st.session_state.initial_recommendation_loaded
    # 대시보드에서 사용하는 세션 상태 이름 (최신 버전으로 반영)
    if 'backtest_results_all_conditions' in st.session_state:
        del st.session_state.backtest_results_all_conditions
    if 'recommended_fund_stocks_latest' in st.session_state:
        del st.session_state.recommended_fund_stocks_latest
    
    if 'show_fund_details' in st.session_state: 
        del st.session_state.show_fund_details
    if 'wobble_triggered' in st.session_state: 
        del st.session_state.wobble_triggered 

    st.session_state.reset_survey_flag = False


# --- 대시보드 데이터 로딩 및 추천 함수 ---

@st.cache_data(ttl=3600) # 데이터 로딩 성능 최적화 (1시간 TTL)
def load_and_process_data(file_path='이거진짜마지막데이터셋.xlsx'): 
    """
    '이거진짜마지막데이터셋.xlsx' 파일을 로드하고 필요한 전처리를 수행합니다.
    - 필수 컬럼 존재 여부 확인
    - 숫자형 컬럼 타입 변환 및 NaN 처리
    - '위험도' 컬럼 계산 (기존 로직 유지)
    - '초과수익률' 컬럼은 사용하지 않도록 코드에서 제거
    - 2017년 이후의 데이터만 필터링
    """
    try:
        df = pd.read_excel(file_path, dtype={'거래소코드': str})
    except FileNotFoundError:
        st.error(f"⚠️ 데이터 파일 '{file_path}'을(를) 찾을 수 없습니다. 프로젝트 루트 디렉토리에 파일을 넣어주세요.")
        st.stop()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        st.stop()
        return pd.DataFrame()

    # 필수 컬럼 정의 ('초과수익률' 제거됨)
    required_cols = [
        '회사명', '거래소코드', '회계년도', '이자보상배율(이자비용)',
        '영업활동으로 인한 현금흐름(*)(천원)', '투자활동으로 인한 현금흐름(*)(천원)',
        '재무활동으로 인한 현금흐름(*)(천원)', '당좌비율', '정상영업이익증가율',
        '순이익증가율', '매출액증가율', '유동자산(*)(천원)', '부채(*)(천원)',
        '당기순이익(손실)(천원)', '산업코드', '산업명', '수정종가',
        '연간변동성', 'EBITDA(천원)', 'x3', 'x4', 'roe', 'pcr',
        'psr', 'ln(매출액)', '잉여현금흐름 비율', 'CAGR', 'target_class' 
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ 데이터 파일 '{file_path}'에 다음 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
        st.stop() 

    # 숫자형 컬럼 변환 및 NaN 처리 ('초과수익률' 제거됨)
    numeric_cols = [
        '이자보상배율(이자비용)', '영업활동으로 인한 현금흐름(*)(천원)',
        '투자활동으로 인한 현금흐름(*)(천원)', '재무활동으로 인한 현금흐름(*)(천원)',
        '당좌비율', '정상영업이익증가율', '순이익증가율', '매출액증가율',
        '유동자산(*)(천원)', '부채(*)(천원)', '당기순이익(손실)(천원)',
        '수정종가', '연간변동성', 'EBITDA(천원)', 'x3', 'x4',
        'roe', 'pcr', 'psr', 'ln(매출액)', '잉여현금흐름 비율', 'CAGR',
        'target_class'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if col in ['연간변동성', 'CAGR']: 
                df[col] = df[col].fillna(0) 
            elif col == 'target_class': 
                 df[col] = df[col].fillna(-1).astype(int) 
        
    if '배당수익률' not in df.columns:
        df['배당수익률'] = np.random.uniform(0, 5, len(df))

    df.dropna(subset=['회사명', '회계년도'], inplace=True) 

    df_processed = df.copy() 
    
    # --- 2017년 이후 데이터만 필터링 ---
    if '회계년도' in df_processed.columns:
        df_processed['회계년도'] = pd.to_numeric(df_processed['회계년도'], errors='coerce')
        df_processed.dropna(subset=['회계년도'], inplace=True) 

        df_processed = df_processed[df_processed['회계년도'] >= 2017].copy()
        if df_processed.empty:
            st.warning("⚠️ 2017년 이후의 유효한 회계년도 데이터가 없어 분석을 수행할 수 없습니다.")
            return pd.DataFrame()
    else:
        st.error("⚠️ '회계년도' 컬럼이 없어 연도별 필터링을 수행할 수 없습니다.")
        return pd.DataFrame()
    # --- 2017년 이후 데이터 필터링 끝 ---

    col_c1, col_c2 = '이자보상배율(이자비용)', '영업활동으로 인한 현금흐름(*)(천원)'
    if col_c1 in df_processed.columns and col_c2 in df_processed.columns:
        df_processed.sort_values(by=['거래소코드', '회계년도'], ascending=True, inplace=True)

        temp_df = df_processed[['거래소코드', '회계년도', col_c1, col_c2]].copy()
        temp_df['C1_flag'] = (temp_df[col_c1].fillna(999) < 1).astype(int) 
        temp_df['C2_flag'] = (temp_df[col_c2].fillna(9999) < 0).astype(int)
        
        temp_df['C1_3yr_sum'] = temp_df.groupby('거래소코드')['C1_flag'].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True) # min_periods=1로 변경
        temp_df['C2_3yr_sum'] = temp_df.groupby('거래소코드')['C2_flag'].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True) # min_periods=1로 변경
        
        temp_df['C1_met'] = (temp_df['C1_3yr_sum'] == 3) 
        temp_df['C2_met'] = (temp_df['C2_3yr_sum'] == 3) 

        conditions = [
            (temp_df['C1_met'] == True) & (temp_df['C2_met'] == True), 
            (temp_df['C1_met'] | temp_df['C2_met']) == True             
        ] 
        choices = [2, 1] 
        temp_df['위험도'] = np.select(conditions, choices, default=0) 
        
        # --- 수정된 부분: NaN 값을 0으로 채워서 행이 제거되지 않도록 함 ---
        temp_df['위험도'] = temp_df['위험도'].fillna(0) # 3년치 데이터가 부족하면 '저위험'(0)으로 간주
        # df_processed.dropna(subset=['위험도'], inplace=True) # 이 줄은 이제 필요 없음, 삭제됨
        # --- 수정된 부분 끝 ---

        df_processed = df_processed.merge(
            temp_df[['거래소코드', '회계년도', '위험도']], 
            on=['거래소코드', '회계년도'], 
            how='left'
        )
        
        # merge 후에 발생할 수 있는 NaN (예: merge 키가 없는 경우)은 계속 제거
        # 하지만 위험도 계산으로 인한 NaN은 이제 없어야 함
        df_processed.dropna(subset=['위험도'], inplace=True) # 이 부분은 남겨둡니다. 혹시 모를 다른 NaN 제거용.
        df_processed['위험도'] = df_processed['위험도'].astype(int)

        risk_map = {0: '저위험', 1: '중위험', 2: '고위험'}
        df_processed['위험도_라벨'] = df_processed['위험도'].map(risk_map)

        df_processed.drop(columns=['C1_flag', 'C2_flag', 'C1_3yr_sum', 'C2_3yr_sum', 'C1_met', 'C2_met'], inplace=True, errors='ignore')
    else:
        st.warning("⚠️ '이자보상배율(이자비용)' 또는 '영업활동으로 인한 현금흐름(*)(천원)' 컬럼이 없어 '위험도'를 계산할 수 없습니다.")

    return df_processed