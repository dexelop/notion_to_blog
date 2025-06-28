# Notion 설정 가이드

## 1. Notion 데이터베이스 생성

### 1.1 새 페이지 생성
1. Notion 워크스페이스에서 새 페이지 생성
2. 페이지 제목: "Blog Database" (또는 원하는 이름)
3. 데이터베이스 선택 → "Table" 선택

### 1.2 데이터베이스 속성 설정
다음 속성들을 추가해주세요:

| 속성명 | 타입 | 설명 | 필수 |
|--------|------|------|------|
| 제목 (Title) | 제목 | 블로그 글 제목 | ✅ |
| 슬러그 (Slug) | 텍스트 | URL 경로 (예: my-first-post) | ✅ |
| 상태 (Status) | 선택 | Draft, Published, Archived | ✅ |
| 발행일 (Published Date) | 날짜 | 게시 날짜 | ❌ |
| 태그 (Tags) | 다중 선택 | 글 분류 태그 | ❌ |
| 메타 설명 (Meta Description) | 텍스트 | SEO용 설명 (160자 이내) | ❌ |
| 커버 이미지 (Cover Image) | 파일 및 미디어 | 대표 이미지 | ❌ |

### 1.3 상태(Status) 옵션 설정
Status 속성에 다음 옵션들을 추가:
- **Draft**: 작성 중
- **Published**: 게시됨
- **Archived**: 보관됨

## 2. Notion Integration 생성

### 2.1 Integration 생성
1. [Notion Developers](https://www.notion.so/my-integrations) 페이지 접속
2. "New integration" 클릭
3. 다음 정보 입력:
   - Name: "Streamlit Blog Integration"
   - Associated workspace: 본인의 워크스페이스 선택
   - Capabilities: Read content 체크

### 2.2 Integration Token 복사
1. Integration 생성 후 "Internal Integration Token" 복사
2. 이 토큰을 `.env` 파일의 `NOTION_TOKEN`에 붙여넣기

### 2.3 데이터베이스에 Integration 연결
1. Blog Database 페이지로 이동
2. 우측 상단 "..." 메뉴 클릭
3. "Add connections" 선택
4. 방금 생성한 "Streamlit Blog Integration" 선택

### 2.4 Database ID 찾기
1. Blog Database 페이지 URL 확인
2. URL 형식: `https://www.notion.so/workspace-name/database-id?v=view-id`
3. `database-id` 부분 복사 (32자리 문자열)
4. 이 ID를 `.env` 파일의 `NOTION_DATABASE_ID`에 붙여넣기

## 3. 환경 변수 설정

### 3.1 .env 파일 생성
```bash
cp .env.example .env
```

### 3.2 .env 파일 편집
```env
NOTION_TOKEN=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NOTION_DATABASE_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 4. 테스트 데이터 생성

### 4.1 샘플 블로그 글 작성
1. Blog Database에 새 항목 추가
2. 다음 정보 입력:
   - 제목: "첫 번째 테스트 글"
   - 슬러그: "first-test-post"
   - 상태: "Published"
   - 발행일: 오늘 날짜
   - 내용: 간단한 테스트 내용 작성

## 5. 연결 테스트

터미널에서 다음 명령어 실행:
```bash
uv run pytest tests/test_config.py -v
```

모든 테스트가 통과하면 Phase 1 설정이 완료된 것입니다!