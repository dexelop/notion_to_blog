"""
메인 홈페이지
Notion-Streamlit 블로그 시스템의 홈페이지
"""
import streamlit as st
from datetime import datetime
from notion_client import NotionClient


def main():
    st.title("🏠 Welcome to my Blog!")
    
    st.markdown("""
    안녕하세요! Notion과 Streamlit으로 구축된 자동화 블로그에 오신 것을 환영합니다.
    
    이 블로그는 Notion에서 글을 작성하면 자동으로 웹사이트에 반영되는 시스템입니다.
    """)
    
    # 최신 글 미리보기
    st.subheader("📝 최신 글")
    
    try:
        client = NotionClient()
        recent_posts = client.fetch_published_posts()
        
        if recent_posts:
            # 최신 3개 글만 표시
            for post in recent_posts[:3]:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**[{post['title']}](pages/1_blog_articles?post={post['slug']})**")
                        if post.get("meta_description"):
                            st.caption(post["meta_description"][:100] + "...")
                        
                        # 태그 표시
                        if post.get("tags"):
                            tag_badges = [f"`{tag}`" for tag in post["tags"][:3]]  # 최대 3개만
                            st.markdown(" ".join(tag_badges))
                    
                    with col2:
                        if st.button("읽기", key=f"home_{post['id']}"):
                            st.switch_page("pages/1_blog_articles.py")
                    
                    st.divider()
            
            # 모든 글 보기 버튼
            if st.button("📖 모든 글 보기", type="primary"):
                st.switch_page("pages/1_blog_articles.py")
        
        else:
            st.info("아직 발행된 글이 없습니다.")
            st.markdown("Notion에서 첫 번째 글을 작성해보세요!")
    
    except Exception as e:
        st.error("블로그 글을 불러오는 중 오류가 발생했습니다.")
        st.caption(f"오류 내용: {str(e)}")
        st.info("Notion 설정을 확인해주세요.")
    
    # 시스템 정보
    st.markdown("---")
    st.subheader("💡 시스템 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **기술 스택:**
        - 🔗 Notion API
        - 🚀 Streamlit
        - 🐍 Python
        - ☁️ fly.io (배포)
        """)
    
    with col2:
        st.markdown("""
        **주요 기능:**
        - ✍️ Notion에서 글 작성
        - 🔄 자동 동기화
        - 🖼️ 이미지 자동 처리
        - 🏷️ 태그 필터링
        """)


def healthcheck():
    """fly.io 헬스체크용 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# URL 라우팅
if "healthz" in st.query_params:
    st.json(healthcheck())
elif __name__ == "__main__":
    main()