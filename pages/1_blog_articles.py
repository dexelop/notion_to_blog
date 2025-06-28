"""
블로그 글 목록 페이지
Notion에서 발행된 글들을 목록으로 표시
"""
import streamlit as st
from datetime import datetime
from notion_client import NotionClient


@st.cache_data(ttl=3600)  # 1시간 캐싱
def load_blog_posts():
    """블로그 글 목록을 로드 (캐싱됨)"""
    client = NotionClient()
    return client.fetch_published_posts()


def format_date(date_str):
    """날짜 문자열을 포맷팅"""
    if not date_str:
        return "날짜 없음"
    
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%Y년 %m월 %d일")
    except:
        return date_str


def main():
    st.title("📝 블로그 글 목록")
    
    # 캐시 새로고침 버튼
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 새로고침"):
            st.cache_data.clear()
            st.rerun()
    
    # 글 목록 로드
    with st.spinner("블로그 글을 불러오는 중..."):
        posts = load_blog_posts()
    
    if not posts:
        st.warning("발행된 글이 없습니다.")
        st.info("Notion에서 글을 작성하고 상태를 'Published'로 설정해주세요.")
        return
    
    # 태그 필터링
    all_tags = set()
    for post in posts:
        all_tags.update(post.get("tags", []))
    
    if all_tags:
        selected_tags = st.multiselect(
            "태그로 필터링:",
            options=sorted(all_tags),
            default=[]
        )
        
        # 태그 필터 적용
        if selected_tags:
            filtered_posts = []
            for post in posts:
                post_tags = post.get("tags", [])
                if any(tag in post_tags for tag in selected_tags):
                    filtered_posts.append(post)
            posts = filtered_posts
    
    # 글 목록 표시
    st.write(f"총 {len(posts)}개의 글이 있습니다.")
    
    for post in posts:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # 제목을 클릭 가능한 링크로 표시
                st.markdown(f"### [{post['title']}](?post={post['slug']})")
                
                # 메타 설명 표시
                if post.get("meta_description"):
                    st.write(post["meta_description"])
                
                # 태그 표시
                if post.get("tags"):
                    tag_badges = [f"`{tag}`" for tag in post["tags"]]
                    st.markdown(" ".join(tag_badges))
            
            with col2:
                # 발행일 표시
                st.write(f"📅 {format_date(post.get('published_date'))}")
                
                # 상세 보기 버튼
                if st.button(f"읽기", key=f"read_{post['id']}"):
                    st.query_params.post = post['slug']
                    st.rerun()
            
            st.divider()


if __name__ == "__main__":
    # URL 파라미터로 특정 글 요청이 있으면 상세 페이지로 이동
    if "post" in st.query_params:
        # 별도 모듈에서 상세 페이지 처리
        from pages.blog_post import show_blog_post
        show_blog_post(st.query_params.post)
    else:
        main()
