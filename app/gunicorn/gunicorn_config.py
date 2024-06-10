# gunicorn_config.py

# 바인드할 소켓 경로
# bind = 'unix:/ndd/app/gunicorn/gunicorn.sock'
bind = '0.0.0.0:8000'

# 워커 수 (프로세스 수)
workers = 2

# 타임아웃 설정 (초 단위)
timeout = 120

# 로그 파일 설정
accesslog = '/log/access.log'
errorlog = '/log/error.log'

# 로그 수준
loglevel = 'info'