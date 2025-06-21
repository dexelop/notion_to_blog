# Notion-Streamlit 블로그 통합 PRD (Product Requirements Document)

## 1. 프로젝트 개요

### 1.1 프로젝트 명
Notion-Streamlit 블로그 자동화 시스템

### 1.2 목적
현재 하드코딩으로 관리하는 Streamlit 블로그를 Notion과 연동하여, Notion에서 글을 작성하면 자동으로 Streamlit 홈페이지에 반영되도록 하는 시스템 구축

### 1.3 현재 상황
- Streamlit으로 구축된 홈페이지 운영 중
- pages 폴더 구조로 여러 페이지 관리
- 블로그 글 수정 시 매번 하드코딩 필요
- Git 연결 및 fly.io 배포 환경 구축 완료

### 1.4 기대 효과
- 블로그 글 작성/수정 시간 90% 단축
- 기술적 지식 없이도 콘텐츠 관리 가능
- 자동화된 배포 프로세스로 휴먼 에러 감소

## 2. 기술 스택 및 요구사항

### 2.1 필수 기술 스택
- **Backend**: Python 3.8+
- **Framework**: Streamlit
- **CMS**: Notion API
- **Library**: notion-client (공식 Python SDK)
- **CI/CD**: GitHub Actions
- **Hosting**: fly.io
- **Version Control**: Git

### 2.2 시스템 요구사항
- Notion API 접근 권한
- GitHub repository 쓰기 권한
- fly.io 배포 권한
- 환경 변수 관리 시스템

## 3. 기능 요구사항

### 3.1 Notion 설정 (우선순위: 높음)

#### 3.1.1 데이터베이스 구조
```
블로그 데이터베이스 속성:
- 제목 (Title): 제목 타입, 필수
- 슬러그 (Slug): 텍스트 타입, URL 경로용, 필수
- 상태 (Status): 선택 타입 [Draft, Published, Archived], 필수
- 발행일 (Published Date): 날짜 타입
- 태그 (Tags): 다중 선택 타입
- 내용 (Content): 페이지 본문
- 메타 설명 (Meta Description): 텍스트 타입, SEO용
- 커버 이미지 (Cover Image): 파일 타입
```

#### 3.1.2 Notion Integration 설정
- Internal Integration 생성
- 블로그 데이터베이스 읽기 권한 부여
- API 키 안전하게 저장

### 3.2 Python 통합 모듈 (우선순위: 높음)

#### 3.2.1 Notion API 연동
```python
# 필수 구현 함수
- init_notion_client(): Notion 클라이언트 초기화
- fetch_published_posts(): 발행된 글 목록 조회
- get_post_by_slug(slug): 특정 글 상세 조회
- convert_blocks_to_markdown(blocks): Notion 블록을 마크다운으로 변환
- process_notion_images(content): 이미지 URL 처리
```

#### 3.2.2 캐싱 전략
- 글 목록: 1시간 캐싱
- 글 내용: 6시간 캐싱
- 이미지: 영구 저장
- 캐시 수동 갱신 기능

### 3.3 이미지 처리 (우선순위: 높음)

#### 3.3.1 문제점
- Notion API 이미지 URL은 1시간 후 만료

#### 3.3.2 해결 방안
```python
# 이미지 처리 프로세스
1. Notion 콘텐츠에서 이미지 URL 추출
2. 이미지 다운로드
3. 로컬 저장소 또는 CDN 업로드
4. 콘텐츠 내 URL 교체
5. 중복 다운로드 방지 로직
```

### 3.4 Streamlit 페이지 구조 (우선순위: 중간)

#### 3.4.1 블로그 목록 페이지
```python
# pages/blog.py
- 발행된 글 목록 표시
- 태그 필터링
- 페이지네이션 (10개씩)
- 검색 기능 (선택사항)
```

#### 3.4.2 블로그 상세 페이지
```python
# pages/blog_post.py
- URL 파라미터로 slug 받기
- 마크다운 렌더링
- 코드 하이라이팅
- 이미지 표시
- 관련 글 추천 (선택사항)
```

### 3.5 자동화 시스템 (우선순위: 높음)

#### 3.5.1 GitHub Actions Workflow
```yaml
# .github/workflows/sync-notion-blog.yml
실행 조건:
- 6시간마다 자동 실행
- 수동 트리거 가능

작업 내용:
1. Notion API로 콘텐츠 조회
2. 변경사항 확인
3. 이미지 처리
4. 파일 생성/업데이트
5. Git 커밋 & 푸시
6. fly.io 배포 트리거
```

#### 3.5.2 환경 변수 설정
```
필수 환경 변수:
- NOTION_TOKEN: Notion API 토큰
- NOTION_DATABASE_ID: 블로그 데이터베이스 ID
- FLY_API_TOKEN: fly.io 배포 토큰
```

### 3.6 에러 처리 및 모니터링 (우선순위: 중간)

#### 3.6.1 에러 처리
- Notion API 연결 실패 시 캐시된 데이터 표시
- 이미지 다운로드 실패 시 원본 URL 유지
- 동기화 실패 시 알림 발송

#### 3.6.2 로깅
- API 호출 횟수 및 응답 시간
- 에러 발생 내역
- 캐시 히트율

## 4. 비기능 요구사항

### 4.1 성능
- 페이지 로드 시간 3초 이내
- API 호출 최소화 (캐싱 활용)
- 동시 사용자 100명 지원

### 4.2 보안
- API 키 환경 변수로 관리
- HTTPS 통신 필수
- 민감 정보 로깅 금지

### 4.3 확장성
- 다국어 지원 가능한 구조
- 커스텀 블록 타입 추가 가능
- 다른 CMS로 전환 가능한 추상화

## 5. 개발 단계별 작업

### Phase 1: 기초 설정 (1주)
1. Notion 데이터베이스 생성 및 구조 설정
2. Notion Integration 생성 및 권한 설정
3. 개발 환경 구축 (Python 패키지 설치)
4. 환경 변수 설정

### Phase 2: 핵심 기능 개발 (2주)
1. Notion API 연동 모듈 개발
2. 콘텐츠 변환 로직 구현 (Notion → Markdown)
3. 이미지 처리 시스템 구축
4. Streamlit 블로그 페이지 개발

### Phase 3: 자동화 구축 (1주)
1. GitHub Actions workflow 작성
2. 자동 동기화 로직 구현
3. fly.io 배포 연동
4. 에러 처리 및 알림 설정

### Phase 4: 테스트 및 최적화 (1주)
1. 통합 테스트
2. 성능 최적화 (캐싱 튜닝)
3. 에러 시나리오 테스트
4. 문서화

## 6. 테스트 계획

### 6.1 단위 테스트
- Notion API 연동 함수
- 마크다운 변환 로직
- 이미지 처리 함수

### 6.2 통합 테스트
- 전체 동기화 프로세스
- 캐싱 동작
- 에러 복구 시나리오

### 6.3 사용자 테스트
- 글 작성 → 게시 시간 측정
- 다양한 콘텐츠 타입 테스트
- 동시 접속 부하 테스트

## 7. 배포 계획

### 7.1 개발 환경
- 로컬 Streamlit 서버
- 테스트용 Notion 데이터베이스

### 7.2 스테이징 환경
- fly.io 스테이징 앱
- 실제와 동일한 구성

### 7.3 프로덕션 배포
- 점진적 롤아웃
- 롤백 계획 수립
- 모니터링 강화

## 8. 유지보수 계획

### 8.1 정기 작업
- 월 1회 의존성 업데이트
- 분기별 성능 리뷰
- 캐시 정책 검토

### 8.2 모니터링
- API 사용량 추적
- 에러율 모니터링
- 사용자 피드백 수집

## 9. 리스크 및 대응 방안

### 9.1 기술적 리스크
| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| Notion API 제한 | 높음 | 적극적 캐싱, 요청 최적화 |
| 이미지 URL 만료 | 높음 | 로컬 저장 또는 CDN 활용 |
| 동기화 실패 | 중간 | 재시도 로직, 수동 트리거 |
| 성능 저하 | 중간 | 캐싱 강화, 페이지네이션 |

### 9.2 운영 리스크
- Notion 서비스 장애 → 캐시된 콘텐츠로 서비스 유지
- fly.io 장애 → 다른 호스팅으로 긴급 전환 계획

## 10. 성공 지표

### 10.1 정량적 지표
- 글 작성 시간: 30분 → 5분 (83% 감소)
- 배포 시간: 10분 → 자동화 (100% 감소)
- 에러율: 1% 미만
- 페이지 로드 시간: 3초 이내

### 10.2 정성적 지표
- 사용자 만족도
- 콘텐츠 발행 빈도 증가
- 기술 부채 감소

## 11. 참고 자료

### 11.1 필수 문서
- [Notion API 공식 문서](https://developers.notion.com/)
- [Streamlit 문서](https://docs.streamlit.io/)
- [fly.io 배포 가이드](https://fly.io/docs/)

### 11.2 라이브러리
- notion-client: Notion 공식 Python SDK
- streamlit: 웹 앱 프레임워크
- python-dotenv: 환경 변수 관리

### 11.3 예제 코드
- [GitHub: streamlit-notion-connection](https://github.com/dnplus/streamlit-notion-connection)
- [Notion API Python 예제](https://github.com/ramnes/notion-sdk-py)

---

**문서 버전**: 1.0  
**작성일**: 2025-01-21  
**작성자**: [작성자명]  
**승인자**: [승인자명]