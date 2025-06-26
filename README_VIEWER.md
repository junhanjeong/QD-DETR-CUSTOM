# QD-DETR Video Moment Viewer

QD-DETR 데이터셋의 비디오 하이라이트 모멘트를 시각적으로 탐색하고 확인할 수 있는 Streamlit 웹 애플리케이션입니다.

## 주요 기능

### 🎬 비디오 모멘트 시각화
- **원본 쿼리 표시**: 영어 원문 쿼리를 표시
- **한국어 번역**: Google Translate API를 사용한 자동 번역
- **YouTube 비디오 임베드**: 해당 YouTube 비디오를 직접 재생
- **정답 모멘트 구간**: 시간 형식(mm:ss)으로 구간 정보 표시

### 📊 데이터 탐색
- **페이지네이션**: 대량의 데이터를 페이지별로 효율적 탐색
- **검색 기능**: 쿼리 내용으로 필터링 가능
- **다중 데이터셋 지원**: Train/Validation 데이터 선택 가능

### 🎯 정확한 시간 계산
- **VID 파싱**: `youtube_id_start_end` 형식의 VID에서 정보 추출
- **실제 시간 계산**: 클립 내 상대 시간 + 비디오 시작 시간 = 전체 영상 절대 시간
- **바로가기 링크**: 정답 구간으로 바로 이동할 수 있는 YouTube 링크 제공

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements_streamlit.txt
```

### 2. 애플리케이션 실행
```bash
# 기본 버전
streamlit run video_viewer_app.py

# 개선된 버전 (추천)
streamlit run video_viewer_app_enhanced.py
```

### 3. 웹 브라우저에서 접속
- 로컬: http://localhost:8501 (또는 8502)
- 네트워크: 터미널에 표시된 Network URL 사용

## 데이터 형식

애플리케이션은 다음과 같은 JSONL 형식의 데이터를 처리합니다:

```json
{
  "qid": 2579,
  "query": "A girl and her mother cooked while talking with each other on facetime.",
  "duration": 150,
  "vid": "NUsG9BgSes0_210.0_360.0",
  "relevant_clip_ids": [41, 42, 43, ...],
  "saliency_scores": [[1, 1, 2], [1, 1, 3], ...],
  "relevant_windows": [[82, 150]]
}
```

### VID 형식 설명
- 형식: `{youtube_id}_{start_time}_{end_time}`
- 예시: `NUsG9BgSes0_210.0_360.0`
  - YouTube ID: `NUsG9BgSes0`
  - 시작 시간: `210.0`초 (3분 30초)
  - 종료 시간: `360.0`초 (6분)

### 시간 계산 방법
1. **클립 내 상대 시간**: `relevant_windows`에서 제공되는 [start, end] 값
2. **전체 영상 절대 시간**: VID의 start_time + relevant_windows의 시간
3. **최종 YouTube 링크**: `https://www.youtube.com/watch?v={youtube_id}&t={절대_시간}s`

## 사용법

### 1. 데이터 선택
- 사이드바에서 "Validation 데이터" 또는 "Train 데이터" 선택

### 2. 페이지 설정
- "페이지당 아이템 수"로 한 번에 표시할 항목 수 조절 (1-10개)

### 3. 검색
- 사이드바 검색창에 키워드 입력하여 쿼리 필터링

### 4. 탐색
- 페이지 네비게이션 버튼으로 이동
- 각 항목의 YouTube 비디오 직접 재생
- "구간 바로가기" 링크로 정답 모멘트로 이동

## 기능 설명

### 자동 번역
- Google Translate API를 사용하여 영어 쿼리를 한국어로 자동 번역
- 번역 결과는 캐시되어 재번역 방지

### YouTube 통합
- VID에서 추출한 YouTube ID로 비디오 자동 임베드
- 정답 구간 시작 시간으로 비디오 자동 시작
- 외부 YouTube 링크로 전체 화면 재생 가능

### 시간 표시
- mm:ss 형식으로 사용자 친화적 시간 표시
- 클립 내 상대 시간과 전체 영상 절대 시간 모두 표시

## 파일 구조

```
qd-detr-custom/
├── video_viewer_app.py          # 기본 Streamlit 앱
├── video_viewer_app_enhanced.py # 개선된 Streamlit 앱 (추천)
├── requirements_streamlit.txt   # 의존성 패키지 목록
├── data/
│   ├── highlight_val_release.jsonl   # 검증 데이터
│   └── highlight_train_release.jsonl # 훈련 데이터
└── README_VIEWER.md            # 이 파일
```

## 트러블슈팅

### 1. 번역이 작동하지 않는 경우
- 인터넷 연결 확인
- Google Translate API 사용량 제한 확인

### 2. YouTube 비디오가 재생되지 않는 경우
- 해당 YouTube 비디오가 임베드를 허용하는지 확인
- 네트워크 방화벽 설정 확인

### 3. 데이터가 로드되지 않는 경우
- `data/` 폴더에 JSONL 파일이 있는지 확인
- 파일 권한 및 인코딩(UTF-8) 확인

## 라이센스

이 프로젝트는 QD-DETR 프로젝트의 일부로 동일한 라이센스를 따릅니다.
