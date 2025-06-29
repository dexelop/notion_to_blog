# 자동화 설정 가이드

Phase 3에서 구축한 자동화 시스템을 설정하는 방법입니다.

## 1. GitHub Actions 환경 변수 설정

GitHub 저장소의 Settings → Secrets and variables → Actions에서 다음 환경 변수를 설정하세요:

### 필수 환경 변수
```
NOTION_TOKEN=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NOTION_DATABASE_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FLY_API_TOKEN=your_fly_api_token_here
```

### 환경 변수 설명
- `NOTION_TOKEN`: Phase 1에서 생성한 Notion Integration 토큰
- `NOTION_DATABASE_ID`: Phase 1에서 생성한 Notion 데이터베이스 ID
- `FLY_API_TOKEN`: fly.io API 토큰 (fly.io 배포용)

## 2. fly.io 설정

### 2.1 fly.io CLI 설치 (로컬)
```bash
# macOS
brew install flyctl

# 또는 curl을 사용
curl -L https://fly.io/install.sh | sh
```

### 2.2 fly.io 로그인
```bash
fly auth login
```

### 2.3 앱 생성
```bash
# fly.toml 파일이 있는 디렉토리에서
fly apps create notion-to-blog  # 원하는 앱 이름으로 변경

# fly.toml의 app 이름을 실제 생성한 이름으로 수정
```

### 2.4 환경 변수 설정
```bash
fly secrets set NOTION_TOKEN=your_notion_token
fly secrets set NOTION_DATABASE_ID=your_database_id
```

### 2.5 API 토큰 생성
```bash
# GitHub Actions용 토큰 생성
fly tokens create deploy

# 출력된 토큰을 GitHub Secrets의 FLY_API_TOKEN에 설정
```

## 3. 동기화 스케줄

### 자동 실행
- **스케줄**: 6시간마다 (UTC 00:00, 06:00, 12:00, 18:00)
- **한국 시간**: 09:00, 15:00, 21:00, 03:00

### 수동 실행
GitHub Actions 탭에서 "Notion Blog 자동 동기화" 워크플로우를 수동으로 실행할 수 있습니다.

### Dry Run 모드
수동 실행 시 "Dry run" 옵션을 체크하면 실제 변경 없이 테스트할 수 있습니다.

## 4. 동작 원리

### 동기화 프로세스
1. **Notion API 조회**: 마지막 동기화 이후 업데이트된 글 확인
2. **이미지 처리**: Notion 이미지를 GitHub 저장소로 다운로드
3. **Git 커밋**: 변경사항을 자동으로 커밋하고 푸시
4. **fly.io 배포**: 새로운 변경사항을 자동으로 배포

### 상태 관리
- `.sync_state.json`: 마지막 동기화 시간 저장 (GitHub Actions에서만 생성)
- 로컬에서는 이 파일이 .gitignore에 포함되어 커밋되지 않음

## 5. 모니터링 및 알림

### 성공 시
- GitHub 이슈로 성공 알림 생성
- 업데이트된 글 수와 처리된 이미지 수 표시

### 실패 시
- GitHub 이슈로 오류 알림 생성
- 상세한 오류 메시지 포함

### 로그 확인
GitHub Actions의 "Actions" 탭에서 각 실행의 상세 로그를 확인할 수 있습니다.

## 6. 수동 테스트

### 로컬에서 테스트
```bash
# 환경 변수 설정 후
python sync_notion.py --dry-run

# 실제 실행
python sync_notion.py
```

### 패키지 설치
```bash
uv pip install -r requirements.txt
```

## 7. 문제 해결

### 일반적인 문제
1. **Notion API 오류**: 토큰과 데이터베이스 ID 확인
2. **이미지 다운로드 실패**: 네트워크 또는 권한 문제
3. **Git 푸시 실패**: GitHub 토큰 권한 확인
4. **fly.io 배포 실패**: API 토큰과 앱 설정 확인

### 디버깅
- GitHub Actions 로그에서 상세한 오류 메시지 확인
- 수동 Dry Run으로 문제 격리
- 로컬에서 스크립트 직접 실행

## 8. 보안 고려사항

- 모든 민감한 정보는 GitHub Secrets에 저장
- fly.io 환경 변수도 암호화되어 관리
- GitHub Actions는 최소 권한으로 실행
- API 토큰은 정기적으로 갱신 권장

이제 자동화 시스템이 완전히 구축되었습니다! 🎉