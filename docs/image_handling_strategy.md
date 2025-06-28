# Notion API 이미지 처리 전략

## 문제점
Notion API로 받은 이미지 URL은 **1시간 후 만료**되어 블로그에서 이미지가 깨지는 문제 발생

## 해결 방안

### 옵션 1: GitHub 저장소에 이미지 저장 (권장) ⭐
**장점:**
- 무료로 이미지 호스팅 가능
- GitHub CDN 활용으로 빠른 로딩
- 버전 관리 가능
- 별도 CDN 설정 불필요

**단점:**
- 저장소 크기 증가
- 대용량 이미지 시 제한 가능

**구현 방법:**
```python
1. images/ 디렉토리 생성
2. Notion 이미지 다운로드
3. 해시값으로 중복 체크
4. images/{year}/{month}/{hash}.{ext} 형태로 저장
5. 콘텐츠 내 URL을 GitHub 경로로 교체
```

### 옵션 2: 외부 CDN 사용 (Cloudinary, S3 등)
**장점:**
- 대용량 이미지 처리 용이
- 이미지 변환 기능 활용 가능

**단점:**
- 추가 비용 발생
- 설정 복잡도 증가
- PRD에서 "외부 CDN 사용 금지" 명시

### 옵션 3: fly.io 정적 파일 서빙
**장점:**
- 배포 환경과 통합
- 추가 설정 최소화

**단점:**
- fly.io 용량 제한
- 백업 전략 필요

## 선택한 방안: GitHub 저장소 활용

### 이미지 처리 프로세스
```python
def process_notion_images(content, page_id):
    """Notion 콘텐츠의 이미지를 처리하고 GitHub 경로로 교체"""
    
    # 1. 이미지 URL 추출
    image_urls = extract_image_urls(content)
    
    # 2. 각 이미지 처리
    for url in image_urls:
        # 3. 이미지 다운로드
        image_data = download_image(url)
        
        # 4. 해시값 생성 (중복 방지)
        image_hash = calculate_hash(image_data)
        
        # 5. 저장 경로 결정
        save_path = f"images/{datetime.now().year}/{datetime.now().month}/{image_hash}{ext}"
        
        # 6. 이미지 저장
        if not os.path.exists(save_path):
            save_image(image_data, save_path)
        
        # 7. URL 교체
        github_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{save_path}"
        content = content.replace(url, github_url)
    
    return content
```

### 디렉토리 구조
```
notion_to_blog/
├── images/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── abc123.jpg
│   │   │   └── def456.png
│   │   └── 02/
│   └── README.md  # 이미지 저장 정책 설명
```

### 이미지 최적화
- 최대 너비: 1200px
- 포맷: WebP 변환 고려 (선택사항)
- 압축: 품질 85% 유지

### 캐싱 전략
- 이미지는 한 번 다운로드 후 영구 저장
- 해시값으로 중복 다운로드 방지
- GitHub Actions에서 자동 커밋

## Phase 2에서 구현할 내용
1. `notion_client.py`에 이미지 처리 함수 추가
2. 이미지 다운로드 및 저장 로직 구현
3. URL 교체 로직 구현
4. 중복 방지 메커니즘 구현