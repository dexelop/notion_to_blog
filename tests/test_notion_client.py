"""
Phase 2: Notion API 연동 테스트
Notion 데이터베이스와의 연동 기능을 검증
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime


class TestNotionClient:
    """Notion API 클라이언트 테스트"""
    
    def test_client_initialization(self):
        """테스트: Notion 클라이언트가 올바르게 초기화되는지 확인"""
        from notion_client import NotionClient
        from config.settings import settings
        
        client = NotionClient()
        assert client is not None
        assert client.token == settings.NOTION_TOKEN
        assert client.database_id == settings.NOTION_DATABASE_ID
    
    @patch('notion_client.Client')
    def test_fetch_published_posts(self, mock_notion_client):
        """테스트: 발행된 글 목록을 올바르게 조회하는지 확인"""
        from notion_client import NotionClient
        
        # Mock 설정
        mock_response = {
            "results": [
                {
                    "id": "test-id-1",
                    "properties": {
                        "제목": {"title": [{"plain_text": "테스트 글 1"}]},
                        "슬러그": {"rich_text": [{"plain_text": "test-post-1"}]},
                        "상태": {"select": {"name": "Published"}},
                        "발행일": {"date": {"start": "2025-01-01"}},
                        "태그": {"multi_select": [{"name": "Python"}, {"name": "Notion"}]}
                    }
                }
            ]
        }
        mock_notion_client.return_value.databases.query.return_value = mock_response
        
        # 테스트 실행
        client = NotionClient()
        posts = client.fetch_published_posts()
        
        # 검증
        assert len(posts) == 1
        assert posts[0]["title"] == "테스트 글 1"
        assert posts[0]["slug"] == "test-post-1"
        assert posts[0]["status"] == "Published"
        assert posts[0]["tags"] == ["Python", "Notion"]
    
    @patch('notion_client.Client')
    def test_get_post_by_slug(self, mock_notion_client):
        """테스트: 슬러그로 특정 글을 조회하는지 확인"""
        from notion_client import NotionClient
        
        # Mock 설정
        mock_response = {
            "results": [{
                "id": "test-id-1",
                "properties": {
                    "제목": {"title": [{"plain_text": "테스트 글"}]},
                    "슬러그": {"rich_text": [{"plain_text": "test-post"}]},
                }
            }]
        }
        mock_notion_client.return_value.databases.query.return_value = mock_response
        
        # 페이지 콘텐츠 Mock
        mock_blocks = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"plain_text": "테스트 내용입니다."}]
                    }
                }
            ]
        }
        mock_notion_client.return_value.blocks.children.list.return_value = mock_blocks
        
        # 테스트 실행
        client = NotionClient()
        post = client.get_post_by_slug("test-post")
        
        # 검증
        assert post is not None
        assert post["title"] == "테스트 글"
        assert post["slug"] == "test-post"
        assert "content" in post
    
    def test_convert_blocks_to_markdown(self):
        """테스트: Notion 블록을 마크다운으로 변환하는지 확인"""
        from notion_client import NotionClient
        
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "제목 1"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "일반 단락입니다."}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "목록 항목"}]
                }
            }
        ]
        
        client = NotionClient()
        markdown = client.convert_blocks_to_markdown(blocks)
        
        expected = "# 제목 1\n\n일반 단락입니다.\n\n- 목록 항목\n\n"
        assert markdown == expected
    
    def test_process_notion_images(self):
        """테스트: Notion 이미지 URL을 처리하는지 확인"""
        from notion_client import NotionClient
        
        content = "이미지가 있습니다: ![alt](https://prod-files-secure.s3.amazonaws.com/test.jpg)"
        
        client = NotionClient()
        processed = client.process_notion_images(content, "test-page-id")
        
        # GitHub URL로 변경되었는지 확인
        assert "https://raw.githubusercontent.com/" in processed
        assert "prod-files-secure.s3.amazonaws.com" not in processed