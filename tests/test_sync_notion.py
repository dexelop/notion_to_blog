"""
Phase 3: Notion 동기화 스크립트 테스트
자동화된 콘텐츠 동기화 기능을 검증
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import os
from pathlib import Path


class TestSyncNotion:
    """Notion 동기화 스크립트 테스트"""
    
    def test_sync_state_management(self):
        """테스트: 동기화 상태 관리"""
        from sync_notion import SyncManager
        
        sync_manager = SyncManager()
        
        # 초기 상태
        last_sync = sync_manager.get_last_sync_time()
        assert last_sync is None or isinstance(last_sync, datetime)
        
        # 동기화 시간 업데이트
        now = datetime.now()
        sync_manager.update_last_sync_time(now)
        
        # 업데이트된 시간 확인
        updated_time = sync_manager.get_last_sync_time()
        assert updated_time == now
    
    @patch('sync_notion.NotionClient')
    def test_fetch_updated_posts(self, mock_notion_client):
        """테스트: 업데이트된 글 목록 조회"""
        from sync_notion import SyncManager
        
        # Mock 설정
        mock_posts = [
            {
                "id": "test-1",
                "title": "새 글",
                "slug": "new-post",
                "last_edited": "2025-01-21T10:00:00Z"
            },
            {
                "id": "test-2", 
                "title": "오래된 글",
                "slug": "old-post",
                "last_edited": "2025-01-20T10:00:00Z"
            }
        ]
        mock_notion_client.return_value.fetch_published_posts.return_value = mock_posts
        
        sync_manager = SyncManager()
        
        # 기준 시간 설정 (2025-01-20 12:00:00)
        cutoff_time = datetime(2025, 1, 20, 12, 0, 0)
        
        updated_posts = sync_manager.fetch_updated_posts(cutoff_time)
        
        # 기준 시간 이후에 수정된 글만 반환되어야 함
        assert len(updated_posts) == 1
        assert updated_posts[0]["title"] == "새 글"
    
    def test_git_operations(self):
        """테스트: Git 작업 (add, commit, push)"""
        from sync_notion import GitManager
        
        git_manager = GitManager()
        
        # Git 상태 확인
        assert git_manager.check_git_status() is not None
        
        # 변경사항이 있는지 확인
        has_changes = git_manager.has_changes()
        assert isinstance(has_changes, bool)
    
    @patch('sync_notion.requests.post')
    def test_notification_system(self, mock_post):
        """테스트: 알림 시스템"""
        from sync_notion import NotificationManager
        
        mock_post.return_value.status_code = 200
        
        notification_manager = NotificationManager()
        
        # 성공 알림
        result = notification_manager.send_success_notification(
            posts_count=5,
            images_count=3
        )
        assert result is True
        
        # 실패 알림
        result = notification_manager.send_error_notification(
            error_message="테스트 오류"
        )
        assert result is True
    
    def test_image_processing_batch(self):
        """테스트: 이미지 일괄 처리"""
        from sync_notion import ImageProcessor
        
        processor = ImageProcessor()
        
        # 테스트용 포스트 데이터
        posts = [
            {
                "id": "test-1",
                "content": "![image](https://notion.so/test1.jpg)"
            },
            {
                "id": "test-2", 
                "content": "![image](https://notion.so/test2.jpg)"
            }
        ]
        
        # 이미지 URL 추출 테스트
        image_urls = processor.extract_all_image_urls(posts)
        assert len(image_urls) == 2
        assert "test1.jpg" in str(image_urls)
        assert "test2.jpg" in str(image_urls)
    
    @patch('sync_notion.subprocess.run')
    def test_deployment_trigger(self, mock_subprocess):
        """테스트: 배포 트리거"""
        from sync_notion import DeploymentManager
        
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Deploy successful"
        
        deployment_manager = DeploymentManager()
        
        # fly.io 배포 트리거
        result = deployment_manager.trigger_fly_deployment()
        assert result is True
        
        # 배포 명령어가 올바르게 호출되었는지 확인
        mock_subprocess.assert_called_once()
    
    def test_sync_workflow_integration(self):
        """테스트: 전체 동기화 워크플로우 통합"""
        from sync_notion import NotionSyncWorkflow
        
        workflow = NotionSyncWorkflow()
        
        # 워크플로우 상태 확인
        assert workflow.is_configured() in [True, False]
        
        # 드라이런 모드 테스트
        summary = workflow.run_sync(dry_run=True)
        
        assert "posts_updated" in summary
        assert "images_processed" in summary
        assert "errors" in summary