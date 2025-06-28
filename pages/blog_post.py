"""
블로그 글 상세 페이지
개별 블로그 글의 전체 내용을 표시
"""
import streamlit as st
from datetime import datetime
from notion_client import NotionClient


@st.cache_data(ttl=21600)  # 6시간 캐싱
def load_blog_post(slug):
    """특정 블로그 글을 로드 (캐싱됨)"""
    client = NotionClient()
    return client.get_post_by_slug(slug)


def format_date(date_str):
    """날짜 문자열을 포맷팅"""
    if not date_str:
        return "날짜 없음"
    
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%Y년 %m월 %d일")
    except:
        return date_str


def show_blog_post(slug):
    """블로그 글 상세 내용을 표시"""
    
    # 뒤로가기 버튼
    if st.button("← 목록으로 돌아가기"):
        st.query_params.clear()
        st.rerun()
    
    # 글 로드
    with st.spinner("블로그 글을 불러오는 중..."):
        post = load_blog_post(slug)
    
    if not post:
        st.error("요청한 글을 찾을 수 없습니다.")
        st.info("URL을 확인하거나 목록에서 다시 선택해주세요.")
        
        if st.button("목록으로 이동"):
            st.query_params.clear()
            st.rerun()
        return
    
    # 글 제목
    st.title(post["title"])
    
    # 메타 정보
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        st.write(f"📅 **발행일:** {format_date(post.get('published_date'))}")
    
    with col2:
        if post.get("tags"):
            tag_badges = [f"`{tag}`" for tag in post["tags"]]
            st.markdown(f"🏷️ **태그:** {' '.join(tag_badges)}")
    
    with col3:
        if post.get("meta_description"):
            st.write(f"📝 **요약:** {post['meta_description']}")
    
    st.divider()
    
    # 글 내용
    if post.get("content"):
        st.markdown(post["content"], unsafe_allow_html=False)
    else:
        st.info("이 글은 아직 내용이 없습니다.")
    
    st.divider()
    
    # 푸터
    st.caption(f"마지막 수정: {format_date(post.get('last_edited'))}")
    
    # 관련 글 추천 (선택사항 - 향후 구현)
    st.markdown("---")
    st.subheader("더 읽어보기")
    
    # 다른 글들 간단히 표시
    client = NotionClient()
    other_posts = client.fetch_published_posts()
    
    # 현재 글 제외
    other_posts = [p for p in other_posts if p["slug"] != slug]
    
    if other_posts:
        # 최신 3개 글만 표시
        for post_item in other_posts[:3]:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**[{post_item['title']}](?post={post_item['slug']})**")
                    if post_item.get("meta_description"):
                        st.caption(post_item["meta_description"][:100] + "...")
                
                with col2:
                    if st.button("읽기", key=f"related_{post_item['id']}"):
                        st.query_params.post = post_item['slug']
                        st.rerun()


def main():
    """직접 접근시 목록으로 리다이렉트"""
    st.info("이 페이지는 직접 접근할 수 없습니다.")
    if st.button("블로그 목록으로 이동"):
        st.switch_page("pages/1_blog_articles.py")


if __name__ == "__main__":
    # URL 파라미터 확인
    if "post" in st.query_params:
        show_blog_post(st.query_params.post)
    else:
        main()