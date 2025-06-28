# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Notion-Streamlit Blog Integration System that automatically fetches blog content from a Notion database and displays it on a Streamlit-based website, with automated deployment to fly.io.

**Important**: This project uses `uv` as the package manager. All Python commands must be run with `uv run` prefix.

## Commands

### Development
```bash
# Install dependencies
uv add -r .requirements.txt

# Run Streamlit app locally
uv run streamlit run app.py
# Access at http://localhost:8501

# Run specific page
uv run streamlit run pages/1_blog_articles.py
```

### Testing
```bash
# Run tests (when implemented)
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_notion_client.py
```

## Architecture

### Core Components (Planned)
1. **Notion Integration Module** (`notion_client.py`)
   - Handles authentication and API calls to Notion
   - Fetches blog posts from specified database
   - Manages content synchronization

2. **Blog Display System** 
   - `app.py`: Main homepage
   - `pages/1_blog_articles.py`: Blog listing page
   - Blog detail pages (dynamically generated)

3. **Image Processing Pipeline**
   - Downloads images from Notion
   - Stores in GitHub repository
   - Serves via GitHub CDN

4. **Automation**
   - GitHub Actions workflow for continuous deployment
   - Scheduled sync with Notion database

### Key Technical Requirements
- Python 3.8+
- **uv** package manager (required for all Python operations)
- Notion API integration with proper authentication
- Streamlit for frontend
- GitHub Actions for CI/CD
- fly.io for hosting
- All images served from GitHub repository (no external CDNs)

## Git Workflow Guidelines (중요!)

**반드시 `my_prompt.md`의 체계적인 워크플로우를 따라주세요:**

### 트리거 명령어
- **"시작!"**: 새 프로젝트 워크플로우 시작 → 이슈 생성 → 기술 계획 → 구현
- **"이어가기!"**: 기존 이슈 기반으로 작업 계속
- **"정리!"**: 현재 작업을 PR로 마무리

### 작업 순서 (시작! 명령 시)
1. **요구사항 분석 및 이슈 생성** - 명확한 체크리스트 포함
2. **기술 계획 수립** - 2-3개 대안 제시, "왜"에 대한 상세 설명
3. **질문 및 확인** - 불명확한 부분 확인 후 사용자 컨펌 대기
4. **TDD 구현** - 테스트 먼저 → 최소 코드 → 리팩터링
5. **단계별 커밋** - 의미 있는 단위로 나누어 커밋
6. **PR 생성** - 전체 작업 과정과 기술적 선택 이유 상세 기록

### 커밋 메시지 규칙
```bash
git commit -m "test: [기능명] 테스트 추가 #[이슈번호]"
git commit -m "feat: [기능명] 기본 구현 #[이슈번호]"
git commit -m "refactor: [기능명] 코드 개선 #[이슈번호]"
```

### 핵심 원칙
- **모든 제안에 "왜"에 대한 설명 필수**
- **TDD 방식으로 구현**
- **최소한의 코드로 최대 효율**
- **사용자 컨펌 후에만 구현 시작**
- **Git 히스토리가 스토리가 되도록**

## Development Status

Current implementation status:
- ✅ Basic Streamlit structure
- ✅ Comprehensive PRD documented
- ⏳ Notion API integration pending
- ⏳ Blog functionality pending
- ⏳ Deployment configuration pending

Refer to `notion-streamlit-blog-prd.md` for complete requirements and specifications.