# Python 3.9 이미지를 기반으로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 패키지들을 requirements.txt에서 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 다운로드 디렉토리 생성
RUN mkdir -p /app/downloads

# 포트 5000 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "app.py"] 