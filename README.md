# SearchCast (팟캐스트 & AI 검색 애플리케이션)
### 이 저장소는 팟캐스트 생성과 AI 기반 검색 기능을 통합한 Flask 기반 웹 애플리케이션입니다. 사용자는 원하는 주제를 입력해 웹에서 관련 정보를 수집하고, 이를 기반으로 AI가 생성한 스크립트와 오디오로 팟캐스트를 제작할 수 있습니다.

# Video
[Watch Video]([https://github.com/bigdefence/SearchCast/blob/main/assets/your-video.mp4]


## 주요 기능
### 🎙 팟캐스트 생성
- AI 모델(예: ChatGPT, Gemini)을 활용한 팟캐스트 스크립트 생성.
- 생성된 스크립트를 오디오로 변환하고 배경 음악 추가.
- 생성된 팟캐스트와 스크립트를 자동 저장하여 다운로드 가능.
### 🔍 AI 기반 검색 엔진
- 텍스트, 이미지, 비디오 플랫폼에서 비동기로 검색.
- 사용자 쿼리와 관련된 콘텐츠를 추출하고 분석.
- 의미론적 검색을 통해 관련성이 높은 결과를 우선 순위로 정렬.
### 🌟 동적 상호작용
- AI 생성 응답을 실시간으로 스트리밍하여 사용자에게 제공.
- 검색 결과와 팟캐스트 링크를 직관적인 인터페이스로 표시.

## 시작하기
### 사전 준비
- Python 3.9+ 필요
- .env 파일에 필요한 API 키와 환경 변수를 설정.

### 설치
1. 저장소 클론:
```bash
git clone https://github.com/your_username/podcast-ai-search.git  
cd podcast-ai-search  
```
2. .env 파일 구성:
필요한 API 키(OpenAI, 검색 엔진 등)와 환경 변수를 추가합니다.

3. 애플리케이션 실행:
```bash
python main.py  
```

4. 브라우저에서 앱 접속:
```bash
http://127.0.0.1:5000
```

## 폴더구조
```plaintext
.  
├── main.py                # 메인 애플리케이션 스크립트  
├── services/              # 백엔드 서비스 통합  
│   ├── search.py          # 검색 및 데이터 처리 로직  
│   └── models.py          # AI 모델 통합  
├── utils/                 # 유틸리티 함수  
│   └── text_processing.py # 쿼리 처리 유틸리티  
├── templates/             # Flask용 HTML 템플릿  
│   └── index.html         # 메인 사용자 인터페이스  
├── static/                # 정적 파일  
│   └── generated_podcasts # 저장된 팟캐스트 디렉토리    
└── .env                   # 환경 변수 설정 파일 (저장소에 포함되지 않음)  
```

## 사용 방법
1. 검색 창에 원하는 주제를 입력합니다.
2. 팟캐스트 스크립트를 생성할 AI 모델을 선택합니다(예: ChatGPT, Gemini).
3. 검색 결과(텍스트, 이미지, 비디오)와 생성된 팟캐스트 세부 정보를 확인합니다.
4. 제공된 링크를 통해 팟캐스트를 다운로드하거나 스트리밍할 수 있습니다.
