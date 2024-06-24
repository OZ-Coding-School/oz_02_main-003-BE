from django.db import models


class CommonDateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # 생성된 시간
    updated_at = models.DateTimeField(auto_now=True)  # 데이터가 업데이트 된 시간

    class Meta:
        abstract = True  # DB에 테이블을 추가하지 마세요.
