"""GPXパーサーサービス"""

import xml.etree.ElementTree as ET
from typing import Final

from src.models.gpx import GpxData, Track, TrackPoint, TrackSegment


# GPX名前空間
GPX_NAMESPACE: Final[str] = "http://www.topografix.com/GPX/1/1"
NAMESPACES: Final[dict[str, str]] = {"gpx": GPX_NAMESPACE}


class GpxParseError(Exception):
    """GPXパースエラー"""

    pass


class GpxParser:
    """GPXファイルパーサー"""

    def parse(self, xml_content: bytes) -> GpxData:
        """GPX XMLコンテンツをパースしてGpxDataを返す"""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise GpxParseError(f"XMLパースエラー: {e}") from e

        creator = root.get("creator")
        tracks = self._parse_tracks(root)

        return GpxData(creator=creator, tracks=tuple(tracks))

    def _parse_tracks(self, root: ET.Element) -> list[Track]:
        """トラック要素をパース"""
        tracks: list[Track] = []

        for trk in root.findall("gpx:trk", NAMESPACES):
            name_elem = trk.find("gpx:name", NAMESPACES)
            name = name_elem.text if name_elem is not None else None

            segments = self._parse_segments(trk)
            tracks.append(Track(name=name, segments=tuple(segments)))

        return tracks

    def _parse_segments(self, trk: ET.Element) -> list[TrackSegment]:
        """セグメント要素をパース"""
        segments: list[TrackSegment] = []

        for trkseg in trk.findall("gpx:trkseg", NAMESPACES):
            points = self._parse_points(trkseg)
            segments.append(TrackSegment(points=tuple(points)))

        return segments

    def _parse_points(self, trkseg: ET.Element) -> list[TrackPoint]:
        """トラックポイント要素をパース"""
        points: list[TrackPoint] = []

        for trkpt in trkseg.findall("gpx:trkpt", NAMESPACES):
            lat_str = trkpt.get("lat")
            lon_str = trkpt.get("lon")

            if lat_str is None or lon_str is None:
                continue

            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                continue

            # 高度
            elevation: float | None = None
            ele_elem = trkpt.find("gpx:ele", NAMESPACES)
            if ele_elem is not None and ele_elem.text:
                try:
                    elevation = float(ele_elem.text)
                except ValueError:
                    pass

            # 時刻
            time: str | None = None
            time_elem = trkpt.find("gpx:time", NAMESPACES)
            if time_elem is not None and time_elem.text:
                time = time_elem.text

            points.append(
                TrackPoint(
                    latitude=latitude,
                    longitude=longitude,
                    elevation=elevation,
                    time=time,
                )
            )

        return points
