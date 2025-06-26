import streamlit as st
import json
import pandas as pd
from googletrans import Translator
import re
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="QD-DETR Video Moment Viewer", layout="wide")

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
            base_url += f"?start={int(start_time)}"
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

def translate_text(text, target_language='ko'):
    """Google Translate를 사용하여 텍스트를 번역하는 함수"""
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        st.error(f"번역 중 오류 발생: {e}")
        return text

def main():
    st.title("🎬 QD-DETR Video Moment Viewer")
    st.markdown("---")
    
    # 사이드바에서 파일 선택
    st.sidebar.title("설정")
    
    # 기본 파일 경로들
    default_files = {
        "Validation 데이터": "data/highlight_val_release.jsonl",
        "Train 데이터": "data/highlight_train_release.jsonl"
    }
    
    selected_file = st.sidebar.selectbox(
        "데이터 파일 선택:",
        options=list(default_files.keys())
    )
    
    file_path = default_files[selected_file]
    
    # 데이터 로드
    with st.spinner("데이터를 로드하는 중..."):
        data = load_jsonl_data(file_path)
    
    if not data:
        st.error("데이터를 로드할 수 없습니다.")
        return
    
    st.success(f"총 {len(data)}개의 데이터를 로드했습니다.")
    
    # 페이지네이션 설정
    items_per_page = st.sidebar.slider("페이지당 아이템 수", 1, 20, 5)
    total_pages = (len(data) - 1) // items_per_page + 1
    
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    # 페이지 선택
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("이전 페이지") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col2:
        page = st.selectbox(
            "페이지 선택:",
            range(1, total_pages + 1),
            index=st.session_state.page - 1,
            key='page_select'
        )
        st.session_state.page = page
    with col3:
        if st.button("다음 페이지") and st.session_state.page < total_pages:
            st.session_state.page += 1
    
    # 현재 페이지 데이터 계산
    start_idx = (st.session_state.page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(data))
    current_data = data[start_idx:end_idx]
    
    st.markdown(f"**페이지 {st.session_state.page} / {total_pages}** (아이템 {start_idx + 1}-{end_idx} / {len(data)})")
    st.markdown("---")
    
    # 번역 캐시 초기화
    if 'translations' not in st.session_state:
        st.session_state.translations = {}
    
    # 각 데이터 항목 표시
    for i, item in enumerate(current_data):
        actual_idx = start_idx + i + 1
        
        # 기본 정보 추출
        qid = item.get('qid', 'N/A')
        query = item.get('query', '')
        vid = item.get('vid', '')
        relevant_windows = item.get('relevant_windows', [])
        duration = item.get('duration', 0)
        
        # YouTube 정보 추출
        youtube_id = extract_youtube_id_from_vid(vid)
        youtube_url = get_youtube_url(youtube_id)
        video_start_time = get_video_start_time(vid)
        
        # 컨테이너 생성
        with st.container():
            st.markdown(f"### 📋 항목 {actual_idx} (QID: {qid})")
            
            # 2개 컬럼으로 분할
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**🔍 원본 쿼리:**")
                st.info(query)
                
                # 번역된 쿼리
                if query not in st.session_state.translations:
                    with st.spinner("번역 중..."):
                        st.session_state.translations[query] = translate_text(query, 'ko')
                
                st.markdown("**🌐 한국어 번역:**")
                st.success(st.session_state.translations[query])
                
                # 비디오 정보
                st.markdown("**📹 비디오 정보:**")
                st.write(f"- **VID:** `{vid}`")
                st.write(f"- **YouTube ID:** `{youtube_id}`")
                st.write(f"- **비디오 길이:** {duration}초")
                if youtube_url:
                    st.markdown(f"- **YouTube 링크:** [여기서 보기]({youtube_url})")
                
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
                            
                            st.write(f"**구간 {j+1}:**")
                            st.write(f"  - 클립 내: {seconds_to_mmss(start_in_clip)} ~ {seconds_to_mmss(end_in_clip)}")
                            st.write(f"  - 전체 영상: {seconds_to_mmss(actual_start)} ~ {seconds_to_mmss(actual_end)}")
                else:
                    st.write("정답 구간이 없습니다.")
            
            with col2:
                # YouTube 비디오 임베드
                if youtube_id:
                    st.markdown("**🎥 YouTube 비디오:**")
                    
                    # 첫 번째 relevant window의 시작 시간으로 비디오 시작
                    embed_start_time = video_start_time
                    if relevant_windows and len(relevant_windows[0]) >= 2:
                        embed_start_time += relevant_windows[0][0]
                    
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
                                st.markdown(f"[구간 {j+1} 바로가기]({jump_url})")
                else:
                    st.warning("YouTube 비디오를 찾을 수 없습니다.")
            
            st.markdown("---")

if __name__ == "__main__":
    main()
