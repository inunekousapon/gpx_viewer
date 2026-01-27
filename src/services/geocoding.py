"""逆ジオコーディングサービス（Nominatim API）"""

import asyncio
import time
from typing import Any

import httpx
from pydantic import BaseModel


class AddressResult(BaseModel):
    """住所結果"""

    prefecture: str = ""
    city: str = ""
    road: str = ""


class GeocodingService:
    """
    逆ジオコーディングサービス

    - APIリクエストをキューイングして直列実行
    - 1秒に1回以上のリクエストを行わない
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[
            tuple[float, float, asyncio.Future[AddressResult | None]]
        ] = asyncio.Queue()
        self._last_request_time: float = 0.0
        self._min_interval: float = 1.0  # 最小リクエスト間隔（秒）
        self._worker_task: asyncio.Task[None] | None = None
        self._client: httpx.AsyncClient | None = None
        self._cache: dict[str, AddressResult] = {}

    async def _ensure_worker_started(self) -> None:
        """ワーカータスクが起動していることを確認"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        """キューからリクエストを取り出して処理するワーカー"""
        while True:
            try:
                lat, lng, future = await asyncio.wait_for(
                    self._queue.get(), timeout=60.0
                )
            except asyncio.TimeoutError:
                # 60秒間リクエストがなければワーカー終了
                break

            try:
                # レート制限: 前回のリクエストから最低1秒待つ
                elapsed = time.time() - self._last_request_time
                if elapsed < self._min_interval:
                    await asyncio.sleep(self._min_interval - elapsed)

                result = await self._fetch_address(lat, lng)
                self._last_request_time = time.time()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self._queue.task_done()

    async def _fetch_address(self, lat: float, lng: float) -> AddressResult | None:
        """Nominatim APIから住所を取得"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)

        try:
            response = await self._client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "format": "json",
                    "lat": lat,
                    "lon": lng,
                    "zoom": 18,
                    "addressdetails": 1,
                    "accept-language": "ja",
                },
                headers={"User-Agent": "GPXMapViewer/1.0"},
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            address = data.get("address", {})

            return AddressResult(
                prefecture=address.get("province", "")
                or address.get("state", "")
                or "",
                city=address.get("city", "")
                or address.get("town", "")
                or address.get("village", "")
                or address.get("county", "")
                or "",
                road=address.get("road", "")
                or address.get("pedestrian", "")
                or address.get("footway", "")
                or address.get("path", "")
                or "",
            )
        except Exception:
            return None

    async def get_address(self, lat: float, lng: float) -> AddressResult | None:
        """
        住所を取得（キューイングされる）

        Args:
            lat: 緯度
            lng: 経度

        Returns:
            住所結果、またはNone（エラー時）
        """
        # キャッシュキー（小数点5桁で丸める）
        cache_key = f"{lat:.5f},{lng:.5f}"

        # サーバーサイドキャッシュチェック
        if cache_key in self._cache:
            return self._cache[cache_key]

        # ワーカーが起動していることを確認
        await self._ensure_worker_started()

        # Futureを作成してキューに追加
        loop = asyncio.get_event_loop()
        future: asyncio.Future[AddressResult | None] = loop.create_future()
        await self._queue.put((lat, lng, future))

        # 結果を待つ
        result = await future

        # キャッシュに保存
        if result is not None:
            self._cache[cache_key] = result

        return result

    async def close(self) -> None:
        """クライアントをクローズ"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# シングルトンインスタンス
_geocoding_service: GeocodingService | None = None


def get_geocoding_service() -> GeocodingService:
    """ジオコーディングサービスのシングルトンを取得"""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service
