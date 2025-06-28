"""
Notion API 연동 모듈
Notion 데이터베이스에서 블로그 콘텐츠를 조회하고 변환하는 기능 제공
"""
import os
import hashlib
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from notion_client import Client
from config.settings import settings


class NotionClient:
    """Notion API 클라이언트"""
    
    def __init__(self):
        """Notion 클라이언트 초기화"""
        self.client = Client(auth=settings.NOTION_TOKEN)
        self.database_id = settings.NOTION_DATABASE_ID
        self.token = settings.NOTION_TOKEN
    
    def fetch_published_posts(self) -> List[Dict]:
        """
        발행된 블로그 글 목록을 조회
        
        Returns:
            List[Dict]: 발행된 글 목록
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "상태",
                    "select": {
                        "equals": "Published"
                    }
                },
                sorts=[
                    {
                        "property": "발행일",
                        "direction": "descending"
                    }
                ]
            )
            
            posts = []
            for page in response["results"]:
                post = self._extract_page_properties(page)
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"글 목록 조회 오류: {str(e)}")
            return []
    
    def get_post_by_slug(self, slug: str) -> Optional[Dict]:
        """
        슬러그로 특정 글을 조회
        
        Args:
            slug (str): 글의 슬러그
            
        Returns:
            Optional[Dict]: 글 정보 (없으면 None)
        """
        try:
            # 슬러그로 페이지 검색
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "슬러그",
                    "rich_text": {
                        "equals": slug
                    }
                }
            )
            
            if not response["results"]:
                return None
            
            page = response["results"][0]
            post = self._extract_page_properties(page)
            
            # 페이지 콘텐츠 조회
            content_blocks = self.client.blocks.children.list(block_id=page["id"])
            post["content"] = self.convert_blocks_to_markdown(content_blocks["results"])
            post["content"] = self.process_notion_images(post["content"], page["id"])
            
            return post
            
        except Exception as e:
            print(f"글 조회 오류: {str(e)}")
            return None
    
    def _extract_page_properties(self, page: Dict) -> Dict:
        """
        Notion 페이지에서 속성을 추출
        
        Args:
            page (Dict): Notion 페이지 객체
            
        Returns:
            Dict: 추출된 속성들
        """
        properties = page["properties"]
        
        # 제목 추출
        title = ""
        if "제목" in properties and properties["제목"]["title"]:
            title = properties["제목"]["title"][0]["plain_text"]
        
        # 슬러그 추출
        slug = ""
        if "슬러그" in properties and properties["슬러그"]["rich_text"]:
            slug = properties["슬러그"]["rich_text"][0]["plain_text"]
        
        # 상태 추출
        status = ""
        if "상태" in properties and properties["상태"]["select"]:
            status = properties["상태"]["select"]["name"]
        
        # 발행일 추출
        published_date = None
        if "발행일" in properties and properties["발행일"]["date"]:
            published_date = properties["발행일"]["date"]["start"]
        
        # 태그 추출
        tags = []
        if "태그" in properties and properties["태그"]["multi_select"]:
            tags = [tag["name"] for tag in properties["태그"]["multi_select"]]
        
        # 메타 설명 추출
        meta_description = ""
        if "메타 설명" in properties and properties["메타 설명"]["rich_text"]:
            meta_description = properties["메타 설명"]["rich_text"][0]["plain_text"]
        
        return {
            "id": page["id"],
            "title": title,
            "slug": slug,
            "status": status,
            "published_date": published_date,
            "tags": tags,
            "meta_description": meta_description,
            "last_edited": page["last_edited_time"]
        }
    
    def convert_blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """
        Notion 블록을 마크다운으로 변환
        
        Args:
            blocks (List[Dict]): Notion 블록 리스트
            
        Returns:
            str: 변환된 마크다운 텍스트
        """
        markdown_parts = []
        
        for block in blocks:
            block_type = block["type"]
            
            if block_type == "paragraph":
                text = self._extract_rich_text(block["paragraph"]["rich_text"])
                markdown_parts.append(text)
            
            elif block_type == "heading_1":
                text = self._extract_rich_text(block["heading_1"]["rich_text"])
                markdown_parts.append(f"# {text}")
            
            elif block_type == "heading_2":
                text = self._extract_rich_text(block["heading_2"]["rich_text"])
                markdown_parts.append(f"## {text}")
            
            elif block_type == "heading_3":
                text = self._extract_rich_text(block["heading_3"]["rich_text"])
                markdown_parts.append(f"### {text}")
            
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                markdown_parts.append(f"- {text}")
            
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block["numbered_list_item"]["rich_text"])
                markdown_parts.append(f"1. {text}")
            
            elif block_type == "code":
                language = block["code"]["language"]
                text = self._extract_rich_text(block["code"]["rich_text"])
                markdown_parts.append(f"```{language}\n{text}\n```")
            
            elif block_type == "quote":
                text = self._extract_rich_text(block["quote"]["rich_text"])
                markdown_parts.append(f"> {text}")
            
            elif block_type == "image":
                image_url = self._get_image_url(block["image"])
                if image_url:
                    markdown_parts.append(f"![image]({image_url})")
        
        return "\n\n".join(markdown_parts) + "\n\n"
    
    def _extract_rich_text(self, rich_text: List[Dict]) -> str:
        """
        Notion rich text를 일반 텍스트로 변환
        
        Args:
            rich_text (List[Dict]): Notion rich text 객체
            
        Returns:
            str: 변환된 텍스트
        """
        if not rich_text:
            return ""
        
        text_parts = []
        for text_obj in rich_text:
            text = text_obj["plain_text"]
            
            # 스타일 적용
            if text_obj["annotations"]["bold"]:
                text = f"**{text}**"
            if text_obj["annotations"]["italic"]:
                text = f"*{text}*"
            if text_obj["annotations"]["code"]:
                text = f"`{text}`"
            
            # 링크 처리
            if text_obj.get("href"):
                text = f"[{text}]({text_obj['href']})"
            
            text_parts.append(text)
        
        return "".join(text_parts)
    
    def _get_image_url(self, image_block: Dict) -> Optional[str]:
        """
        이미지 블록에서 URL 추출
        
        Args:
            image_block (Dict): Notion 이미지 블록
            
        Returns:
            Optional[str]: 이미지 URL
        """
        if image_block["type"] == "file":
            return image_block["file"]["url"]
        elif image_block["type"] == "external":
            return image_block["external"]["url"]
        return None
    
    def process_notion_images(self, content: str, page_id: str) -> str:
        """
        Notion 이미지 URL을 GitHub 저장소 URL로 교체
        
        Args:
            content (str): 마크다운 콘텐츠
            page_id (str): Notion 페이지 ID
            
        Returns:
            str: 이미지 URL이 교체된 콘텐츠
        """
        import re
        
        # 이미지 URL 패턴 찾기
        image_pattern = r'!\[([^\]]*)\]\((https://[^)]+)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            original_url = match.group(2)
            
            # Notion 이미지 URL인지 확인
            if "prod-files-secure.s3.amazonaws.com" in original_url or "notion.so" in original_url:
                # 이미지 다운로드 및 저장
                local_path = self._download_and_save_image(original_url, page_id)
                if local_path:
                    # GitHub raw URL로 변환
                    github_url = f"https://raw.githubusercontent.com/dexelop/notion_to_blog/main/{local_path}"
                    return f"![{alt_text}]({github_url})"
            
            return match.group(0)  # 원본 반환
        
        return re.sub(image_pattern, replace_image, content)
    
    def _download_and_save_image(self, url: str, page_id: str) -> Optional[str]:
        """
        이미지를 다운로드하고 로컬에 저장
        
        Args:
            url (str): 이미지 URL
            page_id (str): Notion 페이지 ID
            
        Returns:
            Optional[str]: 저장된 파일 경로
        """
        try:
            # 이미지 다운로드
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 파일 확장자 추출
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'  # 기본값
            
            # 파일 해시 생성 (중복 방지)
            image_hash = hashlib.md5(response.content).hexdigest()[:16]
            
            # 저장 경로 생성
            now = datetime.now()
            year = now.year
            month = f"{now.month:02d}"
            
            save_dir = Path(f"images/{year}/{month}")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{image_hash}{ext}"
            file_path = save_dir / filename
            
            # 이미 존재하면 기존 파일 사용
            if file_path.exists():
                return str(file_path)
            
            # 파일 저장
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return str(file_path)
            
        except Exception as e:
            print(f"이미지 다운로드 오류: {str(e)}")
            return None