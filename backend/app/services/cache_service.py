"""
캐시 서비스 (선택적)
- Redis가 설정되어 있으면 Redis 캐시 사용
- 없으면 메모리 기반 LRU 캐시로 동작
- 확장 포인트: Redis Cluster, Memcached 교체 가능
"""
import json
import hashlib
import logging
from typing import Optional, Any
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    캐시 추상 레이어

    확장 포인트:
    - Redis가 준비되면 REDIS_URL 환경변수만 설정하면 자동 전환
    - TTL 정책 세분화 가능 (장소 목록 vs 상세 정보 vs 챗봇 응답)
    """

    def __init__(self):
        self._redis = None
        self._memory_cache: dict = {}
        self._ttl: int = settings.CACHE_TTL

        if settings.REDIS_URL:
            self._init_redis()

    def _init_redis(self):
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info(f"Redis 캐시 연결: {settings.REDIS_URL}")
        except ImportError:
            logger.warning("redis 패키지 미설치 - 메모리 캐시로 동작")
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e} - 메모리 캐시로 동작")

    @staticmethod
    def make_key(prefix: str, *args) -> str:
        """캐시 키 생성"""
        raw = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(raw.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        try:
            if self._redis:
                val = await self._redis.get(key)
                return json.loads(val) if val else None
            return self._memory_cache.get(key)
        except Exception as e:
            logger.debug(f"캐시 GET 실패: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시 저장"""
        try:
            ttl = ttl or self._ttl
            if self._redis:
                await self._redis.setex(key, ttl, json.dumps(value, ensure_ascii=False))
            else:
                # 메모리 캐시: 간단한 크기 제한 (1000개)
                if len(self._memory_cache) > 1000:
                    oldest_key = next(iter(self._memory_cache))
                    del self._memory_cache[oldest_key]
                self._memory_cache[key] = value
        except Exception as e:
            logger.debug(f"캐시 SET 실패: {e}")

    async def delete(self, key: str) -> None:
        """캐시 삭제"""
        try:
            if self._redis:
                await self._redis.delete(key)
            else:
                self._memory_cache.pop(key, None)
        except Exception as e:
            logger.debug(f"캐시 DELETE 실패: {e}")

    @property
    def is_redis(self) -> bool:
        return self._redis is not None


# 싱글톤 인스턴스
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
