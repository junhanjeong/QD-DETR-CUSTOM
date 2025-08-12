import streamlit as st
import json
import pandas as pd
from googletrans import Translator
import re
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="QD-DETR Video Moment Viewer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .item-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fafafa;
    }
    .query-original {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
    }
    .query-translated {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
    .moment-info {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
    }
    .video-info {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_jsonl_data(file_path):
    """JSONL 파일을 로드하는 함수"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return []
    return data

def extract_youtube_id_from_vid(vid):
    """vid에서 YouTube ID를 추출하는 함수"""
    # vid 형식: "NUsG9BgSes0_210.0_360.0"에서 "_" 이전 부분이 YouTube ID
    parts = vid.split('_')
    if len(parts) >= 2:
        return parts[0]
    return None

def get_youtube_url(youtube_id):
    """YouTube ID로부터 YouTube URL을 생성하는 함수"""
    if youtube_id:
        return f"https://www.youtube.com/watch?v={youtube_id}"
    return None

def get_youtube_embed_url(youtube_id, start_time=None):
    """YouTube 임베드 URL을 생성하는 함수"""
    if youtube_id:
        base_url = f"https://www.youtube.com/embed/{youtube_id}"
        if start_time:
            base_url += f"?start={int(start_time)}&autoplay=1"
        return base_url
    return None

def seconds_to_mmss(seconds):
    """초를 mm:ss 형식으로 변환하는 함수"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_video_start_time(vid):
    """vid에서 비디오 시작 시간을 추출하는 함수"""
    # vid 형식: "NUsG9BgSes0_210.0_360.0"에서 두 번째 숫자가 시작 시간
    parts = vid.split('_')
    if len(parts) >= 2:
        try:
            return float(parts[1])
        except ValueError:
            return 0.0
    return 0.0

@st.cache_data
def translate_text(text, target_language='ko'):
    """Google Translate를 사용하여 텍스트를 번역하는 함수"""
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        return f"번역 실패: {text}"

def display_video_info(item, idx):
    """비디오 정보를 표시하는 함수"""
    qid = item.get('qid', 'N/A')
    query = item.get('query', '')
    vid = item.get('vid', '')
    relevant_windows = item.get('relevant_windows', [])
    duration = item.get('duration', 0)
    
    # YouTube 정보 추출
    youtube_id = extract_youtube_id_from_vid(vid)
    youtube_url = get_youtube_url(youtube_id)
    video_start_time = get_video_start_time(vid)
    
    # 메인 헤더
    st.markdown(f"""
    <div class="item-container">
        <h3>📋 항목 {idx} (QID: {qid})</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 컬럼 분할
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 원본 쿼리
        st.markdown(f"""
        <div class="query-original">
            <h4>🔍 원본 쿼리</h4>
            <p>{query}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 번역된 쿼리
        with st.spinner("번역 중..."):
            translated_query = translate_text(query, 'ko')
        
        st.markdown(f"""
        <div class="query-translated">
            <h4>🌐 한국어 번역</h4>
            <p>{translated_query}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 비디오 정보
        st.markdown(f"""
        <div class="video-info">
            <h4>📹 비디오 정보</h4>
            <p><strong>VID:</strong> <code>{vid}</code></p>
            <p><strong>YouTube ID:</strong> <code>{youtube_id}</code></p>
            <p><strong>비디오 길이:</strong> {duration}초</p>
            <p><strong>YouTube 링크:</strong> <a href="{youtube_url}" target="_blank">여기서 보기</a></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 정답 모멘트 구간
        st.markdown("**⏰ 정답 모멘트 구간:**")
        
        if relevant_windows:
            for j, window in enumerate(relevant_windows):
                if len(window) >= 2:
                    start_in_clip = window[0]
                    end_in_clip = window[1]
                    
                    # 전체 비디오에서의 실제 시간 계산
                    actual_start = video_start_time + start_in_clip
                    actual_end = video_start_time + end_in_clip
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="moment-info">
                            <strong>구간 {j+1}:</strong><br>
                            &nbsp;&nbsp;• 클립 내: {seconds_to_mmss(start_in_clip)} ~ {seconds_to_mmss(end_in_clip)}<br>
                            &nbsp;&nbsp;• 전체 영상: {seconds_to_mmss(actual_start)} ~ {seconds_to_mmss(actual_end)}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="moment-info">
                정답 구간이 없습니다.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # YouTube 비디오 임베드
        if youtube_id:
            st.markdown("#### 🎥 YouTube 비디오")
            
            # VID의 시작 시간으로 비디오 시작
            embed_start_time = video_start_time
            
            embed_url = get_youtube_embed_url(youtube_id, embed_start_time)
            
            # iframe을 사용하여 YouTube 비디오 임베드
            st.markdown(f"""
            <iframe width="100%" height="315" 
                    src="{embed_url}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
            """, unsafe_allow_html=True)
            
            # 시간 점프 버튼들
            if relevant_windows:
                st.markdown("**⏯️ 구간 바로가기:**")
                for j, window in enumerate(relevant_windows):
                    if len(window) >= 2:
                        jump_time = video_start_time + window[0]
                        jump_url = get_youtube_url(youtube_id) + f"&t={int(jump_time)}s"
                        st.markdown(f"🔗 [구간 {j+1} 바로가기]({jump_url})")
        else:
            st.warning("⚠️ YouTube 비디오를 찾을 수 없습니다.")

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🎬 QD-DETR Video Moment Viewer</h1>
        <p>비디오 하이라이트 모멘트를 쉽게 탐색하고 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 기본 파일 경로들
        default_files = {
            "Validation 데이터": "data/highlight_val_release.jsonl",
            "Train 데이터": "data/highlight_train_release.jsonl"
        }
        
        selected_file = st.selectbox(
            "📁 데이터 파일 선택:",
            options=list(default_files.keys()),
            help="분석할 데이터셋을 선택하세요"
        )
        
        file_path = default_files[selected_file]
        
        # 페이지당 아이템 수
        items_per_page = st.slider(
            "📄 페이지당 아이템 수", 
            min_value=1, 
            max_value=10, 
            value=1,
            help="한 페이지에 표시할 아이템 수를 선택하세요"
        )
        
        # 검색 기능
        st.markdown("---")
        st.markdown("#### 🔍 검색")
        search_query = st.text_input(
            "쿼리/QID 검색:",
            placeholder="검색어 또는 QID를 입력하세요...",
            help="쿼리 내용 또는 QID로 검색할 수 있습니다"
        )
    
    # 데이터 로드
    with st.spinner("📊 데이터를 로드하는 중..."):
        data = load_jsonl_data(file_path)
    
    if not data:
        st.error("❌ 데이터를 로드할 수 없습니다.")
        return
    
    # 검색 필터링
    filtered_data = data
    if search_query:
        query_lower = search_query.strip().lower()
        is_numeric = search_query.strip().isdigit()
        if is_numeric:
            # 숫자만 입력된 경우, QID 정확히 일치하는 항목 필터링 (쿼리 텍스트 포함 검색도 유지)
            target_qid = int(search_query.strip())
            filtered_data = [
                item for item in data
                if item.get('qid') == target_qid or query_lower in item.get('query', '').lower()
            ]
        else:
            # 일반 텍스트 검색: 쿼리 내용 부분일치 또는 QID 문자열 부분일치
            filtered_data = [
                item for item in data
                if (query_lower in item.get('query', '').lower())
                or (query_lower in str(item.get('qid', '')))
            ]
        
        # 검색 시 페이지를 1로 리셋
        if 'last_search_query' not in st.session_state:
            st.session_state.last_search_query = ""
        
        if st.session_state.last_search_query != search_query:
            st.session_state.page = 1
            st.session_state.last_search_query = search_query
        
        if not filtered_data:
            st.warning(f"🔍 '{search_query}'에 대한 검색 결과가 없습니다.")
            return
    else:
        # 검색어가 없으면 검색 상태 초기화
        if 'last_search_query' in st.session_state and st.session_state.last_search_query:
            st.session_state.page = 1
            st.session_state.last_search_query = ""
    
    # 상태 정보
    total_items = len(filtered_data)
    st.success(f"✅ 총 {total_items}개의 데이터를 로드했습니다.")
    
    if search_query:
        st.info(f"🔍 검색 결과: {total_items}개 항목 발견")
    
    # 페이지네이션 설정
    total_pages = max(1, (total_items - 1) // items_per_page + 1)
    
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    # 현재 페이지가 유효한 범위에 있는지 확인
    if st.session_state.page > total_pages:
        st.session_state.page = total_pages
    
    # 페이지 네비게이션
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", disabled=st.session_state.page <= 1):
            st.session_state.page -= 1
            st.rerun()
    
    with col2:
        if st.button("⏮️ 처음"):
            st.session_state.page = 1
            st.rerun()
    
    with col3:
        # 페이지 선택 범위 확인
        page_options = list(range(1, total_pages + 1))
        current_page_index = min(st.session_state.page - 1, len(page_options) - 1)
        current_page_index = max(0, current_page_index)
        
        page = st.selectbox(
            "페이지:",
            page_options,
            index=current_page_index,
            key='page_select'
        )
        if page != st.session_state.page:
            st.session_state.page = page
            st.rerun()
    
    with col4:
        if st.button("⏭️ 마지막"):
            st.session_state.page = total_pages
            st.rerun()
    
    with col5:
        if st.button("➡️ 다음", disabled=st.session_state.page >= total_pages):
            st.session_state.page += 1
            st.rerun()
    
    # 현재 페이지 데이터 계산
    start_idx = (st.session_state.page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_data = filtered_data[start_idx:end_idx]
    
    st.markdown(f"**📊 페이지 {st.session_state.page} / {total_pages}** (아이템 {start_idx + 1}-{end_idx} / {total_items})")
    st.markdown("---")
    
    # 각 데이터 항목 표시
    for i, item in enumerate(current_data):
        actual_idx = start_idx + i + 1
        display_video_info(item, actual_idx)
        
        # 구분선
        if i < len(current_data) - 1:
            st.markdown("---")

if __name__ == "__main__":
    main()
