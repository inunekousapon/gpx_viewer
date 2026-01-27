"""GPXパーサーのテスト"""

import pytest

from src.models.gpx import GpxData, Track, TrackPoint, TrackSegment
from src.services.gpx_parser import GpxParser, GpxParseError


class TestGpxParser:
    """GpxParserのテスト"""

    def test_parse_valid_gpx_returns_gpx_data(self) -> None:
        """有効なGPXをパースするとGpxDataが返る"""
        # Arrange
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1">
            <trk>
                <trkseg>
                    <trkpt lat="35.6861" lon="139.6844">
                        <ele>38.9</ele>
                        <time>2025-10-09T20:22:20Z</time>
                    </trkpt>
                </trkseg>
            </trk>
        </gpx>"""
        parser = GpxParser()

        # Act
        result = parser.parse(xml_content)

        # Assert
        assert isinstance(result, GpxData)
        assert result.creator == "Test"
        assert len(result.tracks) == 1

    def test_parse_extracts_track_points(self) -> None:
        """トラックポイントが正しく抽出される"""
        # Arrange
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
            <trk>
                <trkseg>
                    <trkpt lat="35.6861" lon="139.6844">
                        <ele>38.9</ele>
                        <time>2025-10-09T20:22:20Z</time>
                    </trkpt>
                    <trkpt lat="35.6862" lon="139.6845">
                        <ele>40.0</ele>
                    </trkpt>
                </trkseg>
            </trk>
        </gpx>"""
        parser = GpxParser()

        # Act
        result = parser.parse(xml_content)
        points = result.get_all_points()

        # Assert
        assert len(points) == 2
        assert points[0].latitude == pytest.approx(35.6861)
        assert points[0].longitude == pytest.approx(139.6844)
        assert points[0].elevation == pytest.approx(38.9)
        assert points[0].time == "2025-10-09T20:22:20Z"
        assert points[1].time is None

    def test_parse_invalid_xml_raises_error(self) -> None:
        """不正なXMLはGpxParseErrorを発生させる"""
        # Arrange
        xml_content = b"not valid xml"
        parser = GpxParser()

        # Act & Assert
        with pytest.raises(GpxParseError):
            parser.parse(xml_content)

    def test_parse_empty_gpx_returns_empty_tracks(self) -> None:
        """空のGPXは空のトラックリストを返す"""
        # Arrange
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
        </gpx>"""
        parser = GpxParser()

        # Act
        result = parser.parse(xml_content)

        # Assert
        assert len(result.tracks) == 0
        assert len(result.get_all_points()) == 0


class TestGpxData:
    """GpxDataのテスト"""

    def test_get_bounds_returns_correct_bounds(self) -> None:
        """get_boundsが正しい境界を返す"""
        # Arrange
        points = (
            TrackPoint(latitude=35.0, longitude=139.0),
            TrackPoint(latitude=36.0, longitude=140.0),
            TrackPoint(latitude=35.5, longitude=139.5),
        )
        segment = TrackSegment(points=points)
        track = Track(segments=(segment,))
        gpx_data = GpxData(tracks=(track,))

        # Act
        bounds = gpx_data.get_bounds()

        # Assert
        assert bounds is not None
        min_lat, min_lon, max_lat, max_lon = bounds
        assert min_lat == pytest.approx(35.0)
        assert min_lon == pytest.approx(139.0)
        assert max_lat == pytest.approx(36.0)
        assert max_lon == pytest.approx(140.0)

    def test_get_bounds_with_no_points_returns_none(self) -> None:
        """ポイントがない場合get_boundsはNoneを返す"""
        # Arrange
        gpx_data = GpxData()

        # Act
        bounds = gpx_data.get_bounds()

        # Assert
        assert bounds is None

    def test_get_center_returns_correct_center(self) -> None:
        """get_centerが正しい中心を返す"""
        # Arrange
        points = (
            TrackPoint(latitude=35.0, longitude=139.0),
            TrackPoint(latitude=36.0, longitude=140.0),
        )
        segment = TrackSegment(points=points)
        track = Track(segments=(segment,))
        gpx_data = GpxData(tracks=(track,))

        # Act
        center = gpx_data.get_center()

        # Assert
        assert center is not None
        assert center[0] == pytest.approx(35.5)
        assert center[1] == pytest.approx(139.5)
