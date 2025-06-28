"""
환경 설정 관리 모듈
환경 변수를 로드하고 검증하는 기능 제공
"""
import os
from pathlib import Path
from dotenv import load_dotenv


# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """애플리케이션 설정 관리 클래스"""
    
    # Notion 설정
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    # fly.io 설정 (Phase 3에서 사용)
    FLY_API_TOKEN = os.getenv('FLY_API_TOKEN')
    
    @classmethod
    def validate(cls):
        """필수 설정값 검증"""
        errors = []
        
        if not cls.NOTION_TOKEN:
            errors.append("NOTION_TOKEN이 설정되지 않았습니다.")
        
        if not cls.NOTION_DATABASE_ID:
            errors.append("NOTION_DATABASE_ID가 설정되지 않았습니다.")
        
        if errors:
            raise ValueError(f"환경 설정 오류: {', '.join(errors)}")
        
        return True


# 설정 인스턴스
settings = Settings()