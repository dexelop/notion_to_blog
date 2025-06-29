"""
Notion 블로그 자동 동기화 스크립트
GitHub Actions에서 실행되어 Notion 콘텐츠를 자동으로 동기화
"""
import os
import json
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from notion_client import NotionClient
from config.settings import settings


class SyncManager:
    """동기화 상태 관리"""
    
    def __init__(self):
        self.sync_file = Path(".sync_state.json")
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """마지막 동기화 시간 조회"""
        if not self.sync_file.exists():
            return None
        
        try:
            with open(self.sync_file, 'r') as f:
                data = json.load(f)
                last_sync_str = data.get("last_sync")
                if last_sync_str:
                    return datetime.fromisoformat(last_sync_str)
        except Exception as e:
            print(f"동기화 상태 파일 읽기 오류: {e}")
        
        return None
    
    def update_last_sync_time(self, sync_time: datetime):
        """마지막 동기화 시간 업데이트"""
        try:
            data = {
                "last_sync": sync_time.isoformat(),
                "last_sync_readable": sync_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.sync_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"동기화 상태 파일 쓰기 오류: {e}")
    
    def fetch_updated_posts(self, since_time: Optional[datetime] = None) -> List[Dict]:
        """업데이트된 글 목록 조회"""
        client = NotionClient()
        all_posts = client.fetch_published_posts()
        
        if not since_time:
            return all_posts
        
        updated_posts = []
        for post in all_posts:
            last_edited_str = post.get("last_edited")
            if last_edited_str:
                try:
                    last_edited = datetime.fromisoformat(last_edited_str.replace('Z', '+00:00'))
                    # UTC to naive datetime for comparison
                    last_edited = last_edited.replace(tzinfo=None)
                    
                    if last_edited > since_time:
                        updated_posts.append(post)
                except Exception as e:
                    print(f"날짜 파싱 오류: {e}")
                    # 오류 시 포함 (안전장치)
                    updated_posts.append(post)
        
        return updated_posts


class GitManager:
    """Git 작업 관리"""
    
    def check_git_status(self) -> str:
        """Git 상태 확인"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Git 상태 확인 오류: {e}")
            return ""
    
    def has_changes(self) -> bool:
        """변경사항이 있는지 확인"""
        status = self.check_git_status()
        return len(status.strip()) > 0
    
    def add_all_changes(self) -> bool:
        """모든 변경사항을 스테이징"""
        try:
            subprocess.run(["git", "add", "-A"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git add 오류: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """변경사항 커밋"""
        try:
            subprocess.run(["git", "commit", "-m", message], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit 오류: {e}")
            return False
    
    def push_changes(self) -> bool:
        """변경사항 푸시"""
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git push 오류: {e}")
            return False


class ImageProcessor:
    """이미지 일괄 처리"""
    
    def extract_all_image_urls(self, posts: List[Dict]) -> List[str]:
        """모든 포스트에서 이미지 URL 추출"""
        import re
        
        image_urls = []
        image_pattern = r'!\[([^\]]*)\]\((https://[^)]+)\)'
        
        for post in posts:
            content = post.get("content", "")
            matches = re.findall(image_pattern, content)
            for _, url in matches:
                if "prod-files-secure.s3.amazonaws.com" in url or "notion.so" in url:
                    image_urls.append(url)
        
        return image_urls
    
    def process_all_images(self, posts: List[Dict]) -> int:
        """모든 이미지를 처리하고 처리된 개수 반환"""
        client = NotionClient()
        processed_count = 0
        
        for post in posts:
            if post.get("content"):
                original_content = post["content"]
                processed_content = client.process_notion_images(
                    original_content, 
                    post["id"]
                )
                
                # 이미지가 처리되었는지 확인
                if original_content != processed_content:
                    processed_count += len(self.extract_all_image_urls([post]))
        
        return processed_count


class NotificationManager:
    """알림 관리"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = "dexelop"  # GitHub 사용자명
        self.repo_name = "notion_to_blog"
    
    def send_success_notification(self, posts_count: int, images_count: int) -> bool:
        """성공 알림 발송"""
        if not self.github_token:
            print("GitHub 토큰이 없어 알림을 보낼 수 없습니다.")
            return False
        
        message = f"""
🎉 **Notion 블로그 동기화 성공**

- 📝 업데이트된 글: {posts_count}개
- 🖼️ 처리된 이미지: {images_count}개  
- ⏰ 동기화 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

자동화가 정상적으로 작동하고 있습니다! ✅
        """.strip()
        
        return self._create_github_issue(
            title=f"[자동화] 동기화 성공 - {datetime.now().strftime('%m/%d %H:%M')}",
            body=message,
            labels=["automation", "success"]
        )
    
    def send_error_notification(self, error_message: str) -> bool:
        """오류 알림 발송"""
        if not self.github_token:
            print("GitHub 토큰이 없어 알림을 보낼 수 없습니다.")
            return False
        
        message = f"""
❌ **Notion 블로그 동기화 실패**

**오류 내용:**
```
{error_message}
```

**발생 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

수동으로 확인이 필요합니다. 🔧
        """.strip()
        
        return self._create_github_issue(
            title=f"[자동화] 동기화 실패 - {datetime.now().strftime('%m/%d %H:%M')}",
            body=message,
            labels=["automation", "error", "bug"]
        )
    
    def _create_github_issue(self, title: str, body: str, labels: List[str]) -> bool:
        """GitHub 이슈 생성"""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "title": title,
            "body": body,
            "labels": labels
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"GitHub 이슈 생성 성공: {title}")
            return True
        except Exception as e:
            print(f"GitHub 이슈 생성 실패: {e}")
            return False


class DeploymentManager:
    """배포 관리"""
    
    def trigger_fly_deployment(self) -> bool:
        """fly.io 배포 트리거"""
        try:
            # fly.io CLI를 사용한 배포
            result = subprocess.run(
                ["fly", "deploy", "--remote-only"],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("fly.io 배포 성공")
            print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"fly.io 배포 실패: {e}")
            print(f"stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            print("fly CLI가 설치되지 않았습니다.")
            return False


class NotionSyncWorkflow:
    """전체 동기화 워크플로우"""
    
    def __init__(self):
        self.sync_manager = SyncManager()
        self.git_manager = GitManager()
        self.image_processor = ImageProcessor()
        self.notification_manager = NotificationManager()
        self.deployment_manager = DeploymentManager()
    
    def is_configured(self) -> bool:
        """동기화 설정이 완료되었는지 확인"""
        try:
            return bool(settings.NOTION_TOKEN and settings.NOTION_DATABASE_ID)
        except:
            return False
    
    def run_sync(self, dry_run: bool = False) -> Dict:
        """동기화 실행"""
        summary = {
            "posts_updated": 0,
            "images_processed": 0,
            "errors": [],
            "success": False
        }
        
        try:
            print("🔄 Notion 블로그 동기화 시작...")
            
            # 설정 확인
            if not self.is_configured():
                raise Exception("Notion 설정이 완료되지 않았습니다.")
            
            # 마지막 동기화 시간 확인
            last_sync = self.sync_manager.get_last_sync_time()
            if last_sync:
                print(f"📅 마지막 동기화: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("📅 첫 번째 동기화입니다.")
            
            # 업데이트된 글 조회
            updated_posts = self.sync_manager.fetch_updated_posts(last_sync)
            summary["posts_updated"] = len(updated_posts)
            
            print(f"📝 업데이트된 글: {len(updated_posts)}개")
            
            if updated_posts:
                # 이미지 처리
                if not dry_run:
                    images_count = self.image_processor.process_all_images(updated_posts)
                    summary["images_processed"] = images_count
                    print(f"🖼️ 처리된 이미지: {images_count}개")
                
                # Git 작업
                if not dry_run and self.git_manager.has_changes():
                    print("📤 Git 변경사항 커밋 중...")
                    
                    self.git_manager.add_all_changes()
                    
                    commit_message = f"auto: Notion 블로그 동기화 - {len(updated_posts)}개 글 업데이트"
                    self.git_manager.commit_changes(commit_message)
                    self.git_manager.push_changes()
                    
                    print("✅ Git 푸시 완료")
                
                # 배포 트리거 (CI/CD에서 자동 처리되므로 선택적)
                # if not dry_run:
                #     self.deployment_manager.trigger_fly_deployment()
            
            # 동기화 시간 업데이트
            if not dry_run:
                self.sync_manager.update_last_sync_time(datetime.now())
            
            summary["success"] = True
            
            # 성공 알림
            if not dry_run and updated_posts:
                self.notification_manager.send_success_notification(
                    len(updated_posts),
                    summary["images_processed"]
                )
            
            print("🎉 동기화 완료!")
            
        except Exception as e:
            error_msg = str(e)
            summary["errors"].append(error_msg)
            print(f"❌ 동기화 실패: {error_msg}")
            
            # 오류 알림
            if not dry_run:
                self.notification_manager.send_error_notification(error_msg)
        
        return summary


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion 블로그 동기화")
    parser.add_argument("--dry-run", action="store_true", help="실제 변경 없이 테스트")
    
    args = parser.parse_args()
    
    workflow = NotionSyncWorkflow()
    summary = workflow.run_sync(dry_run=args.dry_run)
    
    # 결과 출력
    print("\n📊 동기화 요약:")
    print(f"- 업데이트된 글: {summary['posts_updated']}개")
    print(f"- 처리된 이미지: {summary['images_processed']}개")
    print(f"- 성공 여부: {'✅' if summary['success'] else '❌'}")
    
    if summary['errors']:
        print(f"- 오류: {len(summary['errors'])}개")
        for error in summary['errors']:
            print(f"  • {error}")
    
    # 종료 코드
    exit(0 if summary['success'] else 1)


if __name__ == "__main__":
    main()