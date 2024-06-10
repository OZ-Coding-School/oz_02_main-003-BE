# 베이스 이미지
FROM python:3.12-slim

# 종속성 파일 복사
COPY ./poetry.lock /ndd/
COPY ./pyproject.toml /ndd/

# 작업 디렉토리 설정
WORKDIR /ndd

# 종속성 설치
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN poetry add gunicorn

# 애플리케이션 코드 복사
# COPY ./app /ndd/app
WORKDIR /ndd/app

# 정적 파일 모으기


# 소켓 파일 생성 디렉토리 권한 설정
# RUN mkdir -p /ndd && chmod -R 755 /ndd

# Gunicorn을 사용하여 애플리케이션 실행

COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh
CMD ["/scripts/run.sh"]