"""
Phase 1: 환경 설정 테스트
Notion-Streamlit 블로그 통합을 위한 기본 설정 검증
"""
import os
import pytest
from pathlib import Path


class TestEnvironmentSetup:
    """환경 설정 관련 테스트"""
    
    def test_env_file_exists(self):
        """테스트: .env 파일이 존재하는지 확인"""
        env_path = Path(".env")
        assert env_path.exists(), ".env 파일이 없습니다. .env.example을 참고하여 생성해주세요."
    
    def test_required_env_variables(self):
        """테스트: 필수 환경 변수가 설정되어 있는지 확인"""
        # .env 파일이 있다면 python-dotenv로 로드
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ["NOTION_TOKEN", "NOTION_DATABASE_ID"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        assert not missing_vars, f"필수 환경 변수가 설정되지 않음: {', '.join(missing_vars)}"
    
    def test_env_example_exists(self):
        """테스트: .env.example 파일이 존재하는지 확인"""
        example_path = Path(".env.example")
        assert example_path.exists(), ".env.example 파일이 없습니다."
    
    def test_gitignore_includes_env(self):
        """테스트: .gitignore에 .env가 포함되어 있는지 확인"""
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                assert '.env' in content, ".gitignore에 .env가 포함되어 있지 않습니다."
        else:
            pytest.skip(".gitignore 파일이 없습니다.")


class TestNotionConnection:
    """Notion API 연결 테스트"""
    
    def test_notion_client_import(self):
        """테스트: notion-client 패키지가 설치되어 있는지 확인"""
        try:
            from notion_client import Client
        except ImportError:
            pytest.fail("notion-client 패키지가 설치되어 있지 않습니다.")
    
    def test_notion_client_initialization(self):
        """테스트: Notion 클라이언트 초기화가 가능한지 확인"""
        from notion_client import Client
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("NOTION_TOKEN")
        if not token:
            pytest.skip("NOTION_TOKEN이 설정되지 않아 테스트를 건너뜁니다.")
        
        try:
            client = Client(auth=token)
            assert client is not None
        except Exception as e:
            pytest.fail(f"Notion 클라이언트 초기화 실패: {str(e)}")
    
    @pytest.mark.skip(reason="실제 API 호출은 Phase 2에서 테스트")
    def test_notion_database_access(self):
        """테스트: Notion 데이터베이스 접근이 가능한지 확인"""
        # Phase 2에서 구현 예정
        pass