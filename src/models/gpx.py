"""GPX関連のモデル定義"""

from pydantic import BaseModel, Field, ConfigDict


class TrackPoint(BaseModel):
    """トラックポイント（GPXの1点）"""

    model_config = ConfigDict(frozen=True)

    latitude: float = Field(..., ge=-90, le=90, description="緯度")
    longitude: float = Field(..., ge=-180, le=180, description="経度")
    elevation: float | None = Field(default=None, description="高度(m)")
    time: str | None = Field(default=None, description="時刻(ISO8601)")


class TrackSegment(BaseModel):
    """トラックセグメント"""

    model_config = ConfigDict(frozen=True)

    points: tuple[TrackPoint, ...] = Field(default=(), description="トラックポイントリスト")


class Track(BaseModel):
    """トラック"""

    model_config = ConfigDict(frozen=True)

    name: str | None = Field(default=None, description="トラック名")
    segments: tuple[TrackSegment, ...] = Field(
        default=(), description="セグメントリスト"
    )


class GpxData(BaseModel):
    """GPXデータ全体"""

    model_config = ConfigDict(frozen=True)

    creator: str | None = Field(default=None, description="作成者")
    tracks: tuple[Track, ...] = Field(default=(), description="トラックリスト")

    def get_all_points(self) -> list[TrackPoint]:
        """全トラックポイントをフラットなリストで取得"""
        points: list[TrackPoint] = []
        for track in self.tracks:
            for segment in track.segments:
                points.extend(segment.points)
        return points

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """境界ボックスを取得 (min_lat, min_lon, max_lat, max_lon)"""
        points = self.get_all_points()
        if not points:
            return None

        min_lat = min(p.latitude for p in points)
        max_lat = max(p.latitude for p in points)
        min_lon = min(p.longitude for p in points)
        max_lon = max(p.longitude for p in points)

        return (min_lat, min_lon, max_lat, max_lon)

    def get_center(self) -> tuple[float, float] | None:
        """中心座標を取得"""
        bounds = self.get_bounds()
        if bounds is None:
            return None

        min_lat, min_lon, max_lat, max_lon = bounds
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        return (center_lat, center_lon)
