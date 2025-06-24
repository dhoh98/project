투자성향 진단 및 맞춤형 종목 추천 대시보드
📊 사용자의 투자 성향을 진단하고, 그 결과에 맞춰 저위험/중위험 종목을 추천 및 분석할 수 있는 다중 페이지 Streamlit 웹 애플리케이션입니다.

🌟 주요 기능
투자성향 설문 (Survey)

총 7개의 문항을 통해 사용자의 연령, 투자 기간, 경험, 위험 감수 수준 등을 파악합니다.

문항별 답변 진행률을 실시간으로 시각화하여 보여줍니다.

모든 문항에 답변해야만 결과를 볼 수 있도록 유효성 검사를 수행합니다.

분석 애니메이션 (Analyzing Animation)

설문 제출 후, 결과 페이지로 넘어가기 전 분석이 진행되는 과정을 시뮬레이션 애니메이션으로 보여주어 사용자 경험을 향상시킵니다.

진단 결과 (Result Analysis)

설문 답변을 바탕으로 총점을 계산하고, "안정형"부터 "공격투자형"까지 5가지 투자 유형 중 하나로 분류합니다.

최종 투자 유형과 총점을 시각적으로 강조하여 보여줍니다.

문항별 획득 점수(막대그래프)와 전체 투자성향 분포(게이지 차트)를 Plotly를 통해 시각화합니다.

진단 결과에 따른 투자 유형의 특징과 추천 투자 상품 정보를 제공합니다.

맞춤형 종목 대시보드 (Custom Stock Dashboard)

진단 결과에 따라 위험 등급('저위험', '중위험')이 기본으로 필터링된 종목 리스트를 제공합니다.

사용자는 위험 등급, 정렬 기준(회사명, 배당수익률 등), 정렬 순서를 직접 선택하여 종목을 탐색할 수 있습니다.

종목명 검색 기능으로 원하는 종목을 빠르게 찾을 수 있습니다.

st.data_editor를 활용하여 체크박스로 관심 종목을 포트폴리오에 쉽게 추가/제거할 수 있습니다.

선택된 포트폴리오의 총 초과수익률을 계산하고, 종목별 수익률을 막대그래프로 시각화하여 분석 결과를 제공합니다.

🛠️ 기술 스택
프레임워크: Streamlit

데이터 처리: Pandas, NumPy

데이터 시각화: Plotly

언어: Python

📂 프로젝트 구조
Generated code
.
├── app.py                  # 🏠 메인 애플리케이션 (설문 페이지)
├── pages/
│   ├── 02_analyzing.py     # 🔬 분석 중... 페이지
│   ├── 03_result.py        # 🎯 진단 결과 페이지
│   └── 04_dashboard.py     # 📈 맞춤형 종목 대시보드
├── utils.py                # ⚙️ 공통 함수 모듈 (설문 문항, 점수 계산, 데이터 로딩 등)
├── assets/
│   └── brain_icon.png      # '분석 중' 페이지에서 사용하는 아이콘 이미지
├── dataset1.xlsx           # 💰 종목 분석용 데이터셋
└── requirements.txt        # 📦 필요한 라이브러리 목록
Use code with caution.
⚙️ 설치 및 실행 방법
프로젝트 클론

Generated bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
Use code with caution.
Bash
가상 환경 생성 및 활성화

Generated bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
Use code with caution.
Bash
필요한 라이브러리 설치
아래 내용으로 requirements.txt 파일을 생성하고, 라이브러리를 설치합니다.

requirements.txt

Generated code
streamlit
pandas
numpy
plotly
openpyxl
Use code with caution.
설치 명령어

Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
데이터 파일 준비
프로젝트의 루트 디렉터리에 dataset1.xlsx 파일을 위치시켜야 합니다. 이 파일에는 최소한 다음 컬럼들이 포함되어야 합니다:

거래소코드

회사명

회계년도

이자보상배율(이자비용)

영업활동으로 인한 현금흐름(간접법)(*)(천원)

Streamlit 앱 실행

Generated bash
streamlit run app.py
Use code with caution.
Bash
명령어를 실행하면 웹 브라우저에서 자동으로 애플리케이션이 열립니다.

🔄 애플리케이션 흐름
설문 진행 (app.py): 사용자는 첫 페이지에서 투자 관련 설문에 응답합니다. 모든 답변은 st.session_state에 저장됩니다.

결과 분석 (02_analyzing.py): '진단 결과 보기' 버튼을 클릭하면, 잠시 분석 중 페이지를 거쳐갑니다.

결과 확인 (03_result.py): utils.py의 함수를 통해 점수를 계산하고, 분류된 투자 유형과 상세 분석 차트를 확인합니다.

대시보드 탐색 (04_dashboard.py): '대시보드 보기' 버튼을 클릭하면, 진단 결과에 맞는 필터가 적용된 종목 리스트 페이지로 이동합니다. 사용자는 여기서 종목을 필터링, 정렬, 선택하여 자신만의 포트폴리오를 구성하고 분석할 수 있습니다.