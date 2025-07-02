import streamlit as st
import pandas as pd
import numpy as np

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
            # investment_experience는 다중 선택이므로, 선택된 모든 옵션의 점수 중 최대값을 합산
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


# --- 설문 관련 세션 상태만 초기화 (기존 함수 유지) ---
def reset_survey_state():
    if 'answers' in st.session_state:
        del st.session_state.answers
    if 'survey_completed' in st.session_state:
        del st.session_state.survey_completed
    if 'validation_errors' in st.session_state:
        del st.session_state.validation_errors
    if 'investment_type' in st.session_state:
        del st.session_state.investment_type
    if 'total_score' in st.session_state: # total_score도 초기화
        del st.session_state.total_score
    if 'score_breakdown' in st.session_state: # score_breakdown도 초기화
        del st.session_state.score_breakdown
    
    # 포트폴리오 선택 내역도 함께 초기화
    if 'portfolio_results' in st.session_state:
        del st.session_state.portfolio_results
    if 'show_results' in st.session_state:
        del st.session_state.show_results
    if '포트폴리오 선택' in st.session_state:
        del st.session_state['포트폴리오 선택']
    
    # 추천 펀드 로드 상태 및 애니메이션 상태 초기화 (추가)
    if 'initial_recommendation_loaded' in st.session_state:
        del st.session_state.initial_recommendation_loaded
    if 'recommended_fund_stocks' in st.session_state:
        del st.session_state.recommended_fund_stocks
    if 'show_fund_details' in st.session_state: # 새로 추가된 플래그 초기화
        del st.session_state.show_fund_details
    if 'wobble_triggered' in st.session_state: # 새로 추가된 플래그 초기화
        del st.session_state.wobble_triggered # 이 줄을 추가

    st.session_state.reset_survey_flag = False


# --- 대시보드 데이터 로딩 및 추천 함수 ---

@st.cache_data # 데이터 로딩 성능 최적화
def load_and_process_data(file_path='이거진짜마지막데이터셋.xlsx'): # 파일 경로 변경
    """
    '이거진짜마지막데이터셋.xlsx' 파일을 로드하고 필요한 전처리를 수행합니다.
    - 필수 컬럼 존재 여부 확인
    - 숫자형 컬럼 타입 변환 및 NaN 처리
    - '초과수익률'을 '초과수익률_apply'로 이름 통일
    - '위험도' 컬럼 계산 (기존 로직 유지)
    **이번 버전에서는 각 회사별 최신 회계년도 필터링을 제거하여 모든 연도 데이터를 로드합니다.**
    """
    try:
        df = pd.read_excel(file_path, dtype={'거래소코드': str})
    except FileNotFoundError:
        st.error(f"⚠️ 데이터 파일 '{file_path}'을(를) 찾을 수 없습니다. 프로젝트 루트 디렉토리에 파일을 넣어주세요.")
        st.stop()
        return pd.DataFrame() # 오류 시 빈 DataFrame 반환
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        st.stop()
        return pd.DataFrame()

    # 필수 컬럼 정의 (제공해주신 컬럼 리스트 기반)
    required_cols = [
        '회사명', '거래소코드', '회계년도', '이자보상배율(이자비용)',
        '영업활동으로 인한 현금흐름(*)(천원)', '투자활동으로 인한 현금흐름(*)(천원)',
        '재무활동으로 인한 현금흐름(*)(천원)', '당좌비율', '정상영업이익증가율',
        '순이익증가율', '매출액증가율', '유동자산(*)(천원)', '부채(*)(천원)',
        '당기순이익(손실)(천원)', '산업코드', '산업명', '수정종가',
        '초과수익률', '연간변동성', 'EBITDA(천원)', 'x3', 'x4', 'roe', 'pcr',
        'psr', 'ln(매출액)', '잉여현금흐름 비율', 'CAGR', 'target_class'
    ]
    
    # 필수 컬럼이 데이터셋에 모두 있는지 확인
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ 데이터 파일 '{file_path}'에 다음 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
        st.stop() 

    # 숫자형 컬럼 변환 및 NaN 처리
    numeric_cols = [
        '이자보상배율(이자비용)', '영업활동으로 인한 현금흐름(*)(천원)',
        '투자활동으로 인한 현금흐름(*)(천원)', '재무활동으로 인한 현금흐름(*)(천원)',
        '당좌비율', '정상영업이익증가율', '순이익증가율', '매출액증가율',
        '유동자산(*)(천원)', '부채(*)(천원)', '당기순이익(손실)(천원)',
        '수정종가', '초과수익률', '연간변동성', 'EBITDA(천원)', 'x3', 'x4',
        'roe', 'pcr', 'psr', 'ln(매출액)', '잉여현금흐름 비율', 'CAGR',
        'target_class' # target_class도 숫자형으로 처리
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # 중요한 계산에 사용되는 컬럼은 0으로 채우거나 특정 값으로 처리
            if col in ['연간변동성', 'CAGR', '초과수익률']: # 배당수익률은 제거
                df[col] = df[col].fillna(0) # 0으로 채워 계산 오류 방지
            elif col == 'target_class': # target_class는 정수형으로 유지
                 df[col] = df[col].fillna(-1).astype(int) # 결측치는 -1 등으로 처리 후 정수형으로 변환
        
    # '초과수익률' 컬럼을 '초과수익률_apply'로 이름 통일 (대시보드 코드 호환성)
    if '초과수익률' in df.columns:
        df['초과수익률_apply'] = df['초과수익률']
    elif '초과수익률_apply' not in df.columns: 
        st.warning("⚠️ 경고: '초과수익률' 또는 '초과수익률_apply' 컬럼이 없어 랜덤 값으로 대체합니다.")
        df['초과수익률_apply'] = np.random.uniform(-10, 20, len(df))

    # '배당수익률' 컬럼이 없을 경우 랜덤 값 생성 
    if '배당수익률' not in df.columns:
        df['배당수익률'] = np.random.uniform(0, 5, len(df))

    # '회사명' 컬럼에 NaN 값이 있는 경우 제거
    df.dropna(subset=['회사명', '회계년도'], inplace=True) # 회계년도도 NaN 제거

    # --- 기존에 문제가 되었던, 각 회사별 최신 회계년도만 선택하는 로직을 제거합니다. ---
    # df.sort_values(by=['거래소코드', '회계년도'], ascending=True, inplace=True)
    # df_processed = df.loc[df.groupby('거래소코드')['회계년도'].idxmax()].copy()
    # 이 부분을 삭제함으로써 df_full에는 모든 연도의 데이터가 포함되게 됩니다.
    df_processed = df.copy() # 이제 df_processed는 모든 연도의 데이터를 포함합니다.
    # --- 수정 끝 ---
    
    # 기존 '위험도' 계산 로직 유지
    col_c1, col_c2 = '이자보상배율(이자비용)', '영업활동으로 인한 현금흐름(*)(천원)'
    if col_c1 in df_processed.columns and col_c2 in df_processed.columns:
        # 임시 df를 사용하여 원본 df의 3년 합계를 계산
        temp_df = df_processed.copy() # 모든 연도 데이터가 있는 df_processed 사용
        temp_df['C1_flag'] = (temp_df[col_c1].fillna(999) < 1).astype(int)
        temp_df['C2_flag'] = (temp_df[col_c2].fillna(9999) < 0).astype(int)
        
        # 롤링 윈도우 계산 시 그룹바이를 통해 각 회사별로 적용되도록 함
        temp_df['C1_3yr_sum'] = temp_df.groupby('거래소코드')['C1_flag'].rolling(window=3, min_periods=3).sum().reset_index(level=0, drop=True)
        temp_df['C2_3yr_sum'] = temp_df.groupby('거래소코드')['C2_flag'].rolling(window=3, min_periods=3).sum().reset_index(level=0, drop=True)
        
        # 위험도 계산
        temp_df['C1_met'] = (temp_df['C1_3yr_sum'] == 3)
        temp_df['C2_met'] = (temp_df['C2_3yr_sum'] == 3)

        conditions = [(temp_df['C1_met'] == True) & (temp_df['C2_met'] == True), (temp_df['C1_met'] | temp_df['C2_met']) == True] # OR 조건 수정
        choices = [2, 1]
        temp_df['위험도'] = np.select(conditions, choices, default=0)
        temp_df.loc[temp_df['C1_3yr_sum'].isnull() | temp_df['C2_3yr_sum'].isnull(), '위험도'] = np.nan

        # 최종 df_processed에 '위험도' 컬럼을 병합
        df_processed = df_processed.merge(
            temp_df[['거래소코드', '회계년도', '위험도']], 
            on=['거래소코드', '회계년도'], 
            how='left'
        )
        
        # 위험도 NaN 처리 및 타입 변환
        df_processed.dropna(subset=['위험도'], inplace=True)
        df_processed['위험도'] = df_processed['위험도'].astype(int)

        risk_map = {0: '저위험', 1: '중위험', 2: '고위험'}
        df_processed['위험도_라벨'] = df_processed['위험도'].map(risk_map)

        # 임시로 생성했던 컬럼들 제거 (불필요한 warning 발생 방지)
        df_processed.drop(columns=['C1_flag', 'C2_flag', 'C1_3yr_sum', 'C2_3yr_sum', 'C1_met', 'C2_met'], inplace=True, errors='ignore')
    else:
        st.warning("⚠️ '이자보상배율(이자비용)' 또는 '영업활동으로 인한 현금흐름(*)(천원)' 컬럼이 없어 '위험도'를 계산할 수 없습니다.")


    return df_processed

def get_recommended_stocks(df_raw, investment_type):
    """
    사용자의 투자성향에 따라 종목을 필터링하고 CAGR이 높은 상위 10개 종목을 추천합니다.
    이 함수는 항상 df_raw에서 '최신 연도'의 데이터를 사용하여 추천합니다.
    """
    # 필수 컬럼 확인 (데이터 로드 시 확인했지만, 함수 내에서 다시 한 번 확인)
    required_cols_for_recommendation = ['회계년도', 'target_class', '연간변동성', 'CAGR', '회사명']
    for col in required_cols_for_recommendation:
        if col not in df_raw.columns:
            st.error(f"⚠️ 추천 로직에 필요한 컬럼 '{col}'이(가) 데이터셋에 없습니다. 데이터셋을 확인해주세요.")
            return pd.DataFrame()

    # 가장 최신 연도 데이터만 필터링하여 추천 종목을 선정
    latest_year = df_raw['회계년도'].max()
    if pd.isna(latest_year):
        st.warning("⚠️ 데이터에 유효한 '회계년도' 정보가 없어 종목 추천을 할 수 없습니다.")
        return pd.DataFrame()
        
    df_filtered_by_year = df_raw[df_raw['회계년도'] == latest_year].copy()

    if df_filtered_by_year.empty:
        st.warning(f"⚠️ 최신 연도인 {latest_year}년에 해당하는 데이터가 없어 종목 추천을 할 수 없습니다.")
        return pd.DataFrame()

    # 투자성향별 target_class 매핑
    target_class_map = {
        "안정형": 0,
        "안정추구형": 0, # 안정추구형도 target_class 0을 따르도록
        "위험중립형": 1,
        "적극투자형": 2,
        "공격투자형": 3
    }
    
    current_target_class = target_class_map.get(investment_type, None)

    if current_target_class is None:
        st.warning(f"⚠️ 알 수 없는 투자 유형: '{investment_type}'. 추천 로직을 적용할 수 없습니다.")
        return pd.DataFrame()

    # target_class 기준으로 1차 필터링
    filtered_by_class = df_filtered_by_year[df_filtered_by_year['target_class'] == current_target_class].copy()
    
    if filtered_by_class.empty:
        st.info(f"선택된 '{investment_type}' 유형(target_class: {current_target_class})에 해당하는 종목이 최신 연도 데이터에 없습니다. 다른 종목을 탐색해 보세요.")
        return pd.DataFrame()

    # 연간변동성 분위수 상한 설정
    percentile_upper_bound = 1.0 # 공격투자형 (0~100%)

    if investment_type == "안정형" or investment_type == "안정추구형":
        percentile_upper_bound = 0.25 # 연간변동성 1분위수 (하위 25%)
    elif investment_type == "위험중립형":
        percentile_upper_bound = 0.50 # 연간변동성 50% 분위수 (하위 50%)
    elif investment_type == "적극투자형":
        percentile_upper_bound = 0.75 # 연간변동성 75% 분위수 (하위 75%)
    # 공격투자형은 기본값 1.0 유지

    # 연간변동성 분위수 필터링
    if not filtered_by_class['연간변동성'].empty and filtered_by_class['연간변동성'].nunique() > 1:
        volatility_upper_limit = filtered_by_class['연간변동성'].quantile(percentile_upper_bound)
        filtered_by_volatility = filtered_by_class[filtered_by_class['연간변동성'] <= volatility_upper_limit].copy()
    else: 
        filtered_by_volatility = filtered_by_class 

    if filtered_by_volatility.empty:
        st.info(f"선택된 '{investment_type}' 유형 및 연간변동성 기준에 맞는 종목을 찾지 못했습니다. 다른 종목을 탐색해 보세요.")
        return pd.DataFrame()

    # CAGR 기준으로 내림차순 정렬 후 상위 10개 선택
    filtered_by_volatility['CAGR'] = pd.to_numeric(filtered_by_volatility['CAGR'], errors='coerce').fillna(0)
    
    # 중복된 회사명이 있을 경우 제거 (회계년도 최신값만 가져왔으므로 보통은 중복 없음)
    recommended_stocks = filtered_by_volatility.drop_duplicates(subset=['회사명']).sort_values(by='CAGR', ascending=False).head(10)
    
    if recommended_stocks.empty:
        st.info(f"'{investment_type}' 유형에 대해 추천할 종목을 찾지 못했습니다. 다른 필터 조건을 시도하거나 수동으로 종목을 선택해 보세요.")
    
    return recommended_stocks